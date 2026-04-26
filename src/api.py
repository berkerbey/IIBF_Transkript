import os
import uuid
import shutil
import json
from typing import Dict, List, Any

# Fix for potential OpenMP duplicate library errors
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from src.transcriber import Transcriber
from src.exporters import export_txt, export_docx, export_srt
from src.utils import get_data_path

app = FastAPI(title="SynoptexAI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store for now
# Schema matches the Document Model from implementation_plan
sessions: Dict[str, Any] = {}

# Keep transcriber instances in memory
transcribers: Dict[str, Transcriber] = {}

@app.get("/config")
async def get_config():
    """Reads the config.json file from disk."""
    try:
        config_path = os.path.join(get_data_path(), "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"model_name": "faster-whisper-medium", "device": "cpu", "compute_type": "int8", "default_language": "tr"}

@app.post("/config")
async def save_config(request: Request):
    """Saves the config object to config.json."""
    data = await request.json()
    config_path = os.path.join(get_data_path(), "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return {"status": "success"}

@app.get("/check-model")
async def check_model(model_name: str = "faster-whisper-medium"):
    """Checks if the requested model is already downloaded."""
    from src.transcriber import Transcriber
    path = Transcriber.find_model_path(model_name)
    return {"exists": path is not None}

@app.post("/open-folder")
async def open_output_folder():
    """Opens the output folder in the native file explorer."""
    output_dir = os.path.join(get_data_path(), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    try:
        os.startfile(output_dir)
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """Ingests a file, returns a session ID."""
    session_id = str(uuid.uuid4())
    
    # Save file to a temp directory
    upload_dir = os.path.join(get_data_path(), "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{session_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    sessions[session_id] = {
        "session_id": session_id,
        "metadata": {
            "filename": file.filename,
            "filepath": file_path,
        },
        "state": "READY",
        "transcript": None,
        "insights": []
    }
    
    return {"session_id": session_id, "status": "READY"}

@app.get("/status/{session_id}")
async def get_status(session_id: str):
    """Returns the current state of a session."""
    if session_id not in sessions:
        return {"error": "Session not found", "status": "NOT_FOUND"}
    return sessions[session_id]

def process_audio(session_id: str, model_name: str, language: str, device: str):
    """Background task to run the transcription pipeline."""
    session = sessions.get(session_id)
    if not session:
        return
        
    session["state"] = "PROCESSING"
    session["phase"] = "PREPARING"
    session["percent"] = 0
    filepath = session["metadata"]["filepath"]
    
    try:
        # Load model if not already loaded for this session
        t = Transcriber(model_name=model_name, device=device)
        
        def download_callback(progress_str):
            # Only switch to DOWNLOADING if we actually get a progress string
            session["phase"] = "DOWNLOADING"
            if "%" in progress_str:
                try:
                    percent = int(progress_str.split("%")[0].strip().split()[-1])
                    session["percent"] = percent
                except:
                    pass

        t.load_model(download_callback=download_callback)
        transcribers[session_id] = t
        
        # Switch to TRANSCRIBING phase
        session["phase"] = "TRANSCRIBING"
        session["percent"] = 0
        
        # We enforce word_timestamps=True for the UI sync requirement
        segments_gen, info = t.model.transcribe(
            filepath,
            language=language if language != "auto" else None,
            word_timestamps=True
        )
        
        blocks = []
        for segment in segments_gen:
            words = []
            if segment.words:
                for w in segment.words:
                    words.append({
                        "word": w.word,
                        "start": w.start,
                        "end": w.end,
                        "prob": w.probability
                    })
                    
            blocks.append({
                "id": str(uuid.uuid4()),
                "speaker": "SPEAKER_00", # Placeholder for diarization
                "start_time": segment.start,
                "end_time": segment.end,
                "text": segment.text.strip(),
                "confidence": segment.avg_logprob,
                "words": words
            })
            
            # Update progress percent for TRANSCRIBING
            if info.duration > 0:
                percent = min(99, int((segment.end / info.duration) * 100))
                session["percent"] = percent
            
        session["transcript"] = {
            "language": info.language,
            "duration": info.duration,
            "blocks": blocks
        }
        
        # EXPORT LAYER (Wiring legacy functions)
        base_name = os.path.splitext(session["metadata"]["filename"])[0]
        # Sanitize base_name for directory creation
        safe_base_name = "".join([c for c in base_name if c.isalpha() or c.isdigit() or c == ' ' or c == '-' or c == '_']).strip()
        if not safe_base_name:
            safe_base_name = "transcript_output"
            
        output_dir = os.path.join(get_data_path(), "outputs", safe_base_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare legacy format segments
        legacy_segments = [{"start": b["start_time"], "end": b["end_time"], "text": b["text"]} for b in blocks]
        
        export_txt(legacy_segments, os.path.join(output_dir, f"{safe_base_name}.txt"))
        export_srt(legacy_segments, os.path.join(output_dir, f"{safe_base_name}.srt"))
        export_docx(legacy_segments, os.path.join(output_dir, f"{safe_base_name}.docx"), {"Model": model_name, "Dil": info.language})
        
        # Save transcript.json for history
        file_size = 0
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            
        with open(os.path.join(output_dir, "transcript.json"), "w", encoding="utf-8") as f:
            json.dump({
                "session_id": session_id,
                "filename": session["metadata"]["filename"],
                "filepath": filepath,
                "file_size": file_size,
                "created_at": os.path.getctime(filepath) if os.path.exists(filepath) else 0,
                "transcript": session["transcript"]
            }, f, ensure_ascii=False, indent=2)
        
        # After transcription, we generate mock insights for now
        session["state"] = "ANALYZING"
        # TODO: Implement actual LLM/Clustering logic here
        session["insights"] = [
            {
                "id": str(uuid.uuid4()),
                "type": "THEME",
                "label": "Demo Insight",
                "content": "Analysis layer running successfully.",
                "linked_blocks": []
            }
        ]
        
        session["state"] = "READY"
        
    except Exception as e:
        session["state"] = "ERROR"
        session["error"] = str(e)

@app.post("/transcribe/{session_id}")
async def start_transcription(session_id: str, background_tasks: BackgroundTasks, model: str = "faster-whisper-tiny", lang: str = "auto", device: str = "cpu"):
    """Triggers the asynchronous transcription pipeline."""
    if session_id not in sessions:
        return {"error": "Session not found"}
        
    background_tasks.add_task(process_audio, session_id, model, lang, device)
    return {"message": "Transcription started", "session_id": session_id}

@app.get("/history")
async def get_history():
    """Reads the outputs directory and returns a list of previously processed sessions."""
    history = []
    output_dir = os.path.join(get_data_path(), "outputs")
    if not os.path.exists(output_dir):
        return history
        
    for entry in os.scandir(output_dir):
        if entry.is_dir():
            transcript_file = os.path.join(entry.path, "transcript.json")
            if os.path.exists(transcript_file):
                try:
                    with open(transcript_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Remove the huge block list to send a lightweight history item
                        # Wait, the UI needs the full transcript to load it in the READY screen!
                        # We will send the full object so the UI can reconstruct the completedSession.
                        history.append(data)
                except Exception as e:
                    print(f"Error reading history file {transcript_file}: {e}")
                    
    # Sort by created_at descending
    history.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return history

# Run with: uvicorn src.api:app --reload

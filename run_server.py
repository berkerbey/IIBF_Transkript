import uvicorn
import os
import sys
import multiprocessing

# Add the current directory to sys.path to ensure src is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Required for PyInstaller + multiprocessing
    multiprocessing.freeze_support()
    
    # Environment fixes
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    
    # Default port and host
    host = "127.0.0.1"
    port = 8000
    
    # Allow port/host to be overridden via command line if needed
    for arg in sys.argv:
        if arg.startswith("--port="):
            port = int(arg.split("=")[1])
        if arg.startswith("--host="):
            host = arg.split("=")[1]

    print(f"Starting PAU Transcription Server on {host}:{port}")
    uvicorn.run("src.api:app", host=host, port=port, reload=False, workers=1)

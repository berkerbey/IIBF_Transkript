import os
from faster_whisper import WhisperModel
from src.logger import logger
from src.utils import get_data_path

class Transcriber:
    def __init__(self, model_name="faster-whisper-medium", device="cpu", compute_type="int8"):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.model = None

    @staticmethod
    def find_model_path(model_name: str) -> str | None:
        """
        Return the path/identifier to load the model from, or None if not found locally.
        Search order:
          1. models/models--Systran--{model_name}/snapshots/*/  (HF hub format, project-local)
          2. models/{model_name}/                                (legacy flat folder)
          3. ~/.cache/huggingface/hub/models--Systran--{model_name}/  (global HF cache)
        """
        import pathlib
        data_dir = pathlib.Path(get_data_path())
        cwd = pathlib.Path.cwd()

        # 1. AppData/Local models (Production)
        systran_dir = data_dir / "models" / f"models--Systran--{model_name}"
        if systran_dir.exists():
            snaps = sorted((systran_dir / "snapshots").iterdir()) if (systran_dir / "snapshots").exists() else []
            for snap in reversed(snaps):
                if (snap / "config.json").exists():
                    return str(snap)

        # 2. Project-local models (Development/Fallback)
        systran_dir_local = cwd / "models" / f"models--Systran--{model_name}"
        if systran_dir_local.exists():
            snaps = sorted((systran_dir / "snapshots").iterdir()) if (systran_dir / "snapshots").exists() else []
            for snap in reversed(snaps):  # newest snapshot first
                if (snap / "config.json").exists():
                    return str(snap)

        # 3. Legacy flat folder (AppData)
        flat_dir = data_dir / "models" / model_name
        if flat_dir.exists() and any(flat_dir.iterdir()):
            return str(flat_dir)

        # 4. Legacy flat folder (Local)
        flat_dir_local = cwd / "models" / model_name
        if flat_dir_local.exists() and any(flat_dir_local.iterdir()):
            return str(flat_dir_local)

        # 3. Global HuggingFace hub cache
        hf_hub = pathlib.Path.home() / ".cache" / "huggingface" / "hub"
        if hf_hub.exists():
            for candidate in hf_hub.iterdir():
                if model_name in candidate.name:
                    snaps = sorted((candidate / "snapshots").iterdir()) if (candidate / "snapshots").exists() else []
                    for snap in reversed(snaps):
                        if (snap / "config.json").exists():
                            return model_name.replace("faster-whisper-", "")
        return None

    def load_model(self, download_callback=None):
        """Load the faster-whisper model."""
        short_name = self.model_name.replace("faster-whisper-", "")
        found_path = self.find_model_path(self.model_name)

        if found_path and found_path not in (short_name,):
            path_to_load = found_path
            logger.info(f"Model bulundu, y\u00fckleniyor: {self.model_name}")
        elif found_path:
            path_to_load = short_name
            logger.info(f"Model \u00f6nbellekten y\u00fckleniyor: '{short_name}' (internet gerekmez)")
        else:
            path_to_load = short_name
            logger.info(f"Model ilk kez indiriliyor: '{short_name}' \u2014 l\u00fctfen bekleyin...")



        import sys
        import time
        class TqdmInterceptor:
            def __init__(self, original_stderr, cb):
                self.original_stderr = original_stderr
                self.cb = cb
                self.last_update = 0

            def write(self, s):
                self.original_stderr.write(s)
                if time.time() - self.last_update > 0.1:
                    if "%|" in s or "MB" in s or "kB" in s or "B/s" in s:
                        try:
                            clean_s = s.split('\r')[-1].strip()
                            if clean_s:
                                self.cb(clean_s)
                                self.last_update = time.time()
                        except:
                            pass

            def flush(self):
                self.original_stderr.flush()

        original_stderr = sys.stderr
        if download_callback:
            sys.stderr = TqdmInterceptor(original_stderr, download_callback)

        try:
            # Ensure the models directory exists in AppData
            model_root = os.path.join(get_data_path(), "models")
            os.makedirs(model_root, exist_ok=True)
            
            logger.info(f"Model yükleme dizini: {model_root}")
            
            self.model = WhisperModel(
                path_to_load,
                device=self.device,
                compute_type=self.compute_type,
                download_root=model_root,
                local_files_only=False
            )
            logger.info(f"Yapay zeka modeli başarıyla yüklendi ({self.device} modu).")
            return True
        except Exception as e:
            error_msg = str(e).lower()
            # If it's a CUDA/DLL error and we were trying GPU/Auto, fallback to CPU
            if self.device != "cpu" and ("not found" in error_msg or "cuda" in error_msg or "cublas" in error_msg or "cudnn" in error_msg or "12.dll" in error_msg):
                logger.warning(f"GPU/CUDA hatası alındı, CPU moduna geçiliyor: {str(e)}")
                try:
                    self.model = WhisperModel(
                        path_to_load,
                        device="cpu",
                        compute_type="int8",
                        download_root=model_root,
                        local_files_only=False
                    )
                    logger.info("Yapay zeka modeli CPU modunda başarıyla yüklendi.")
                    return True
                except Exception as e2:
                    logger.error(f"CPU modunda da yükleme hatası: {str(e2)}")
                    return False
            
            logger.error(f"Model yükleme hatası: {str(e)}")
            return False
        finally:
            sys.stderr = original_stderr

    def transcribe(
        self, audio_path: str, language=None, progress_callback=None,
        download_callback=None, normalize=False, initial_prompt=None,
        cancel_event=None
    ):
        """Transcribe an audio file and return a list of segments."""
        if not self.model:
            if not self.load_model(download_callback=download_callback):
                raise Exception("Model yüklenemedi.")

        target_audio = audio_path
        temp_audio = None

        if normalize:
            try:
                import tempfile
                import subprocess
                from src.utils import get_ffmpeg_path
                ffmpeg_exe = get_ffmpeg_path()
                if not os.path.exists(ffmpeg_exe):
                    ffmpeg_exe = "ffmpeg"
                
                logger.info(f"Ses iyileştirme (Normalization) uygulanıyor: {os.path.basename(audio_path)}")
                if progress_callback:
                    progress_callback(0, "Ses kalitesi iyileştiriliyor...")
                
                temp_dir = tempfile.gettempdir()
                temp_audio = os.path.join(temp_dir, f"pau_norm_{os.urandom(4).hex()}.wav")
                
                cmd = [
                    ffmpeg_exe, "-y", "-i", audio_path,
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "16000", "-ac", "1",
                    temp_audio
                ]
                
                # Check for cancellation before heavy processing
                if cancel_event and cancel_event.is_set():
                    logger.info("İşlem iptal edildi.")
                    return [], None

                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                if os.path.exists(temp_audio):
                    target_audio = temp_audio
                else:
                    logger.error("Ses iyileştirme başarısız oldu, orijinal dosya kullanılacak.")
            except Exception as e:
                logger.error(f"Normalizasyon hatası: {e}")

        logger.info(f"Analiz başlatılıyor: {os.path.basename(audio_path)}")
        if language == "auto":
            language = None 
            
        if initial_prompt and str(initial_prompt).strip() == "":
            initial_prompt = None

        try:
            segments, info = self.model.transcribe(
                target_audio,
                language=language,
                beam_size=5,
                vad_filter=True,
                initial_prompt=initial_prompt
            )

            logger.info(f"Tespit edilen dil: '{info.language}' (Olasılık: {info.language_probability:.2f})")

            results = []
            total_duration = info.duration

            for i, segment in enumerate(segments, start=1):
                if cancel_event and cancel_event.is_set():
                    logger.warning("Kullanıcı işlemi iptal etti.")
                    break
                    
                res = {
                    "id": i,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                }
                results.append(res)
                
                if progress_callback and total_duration > 0:
                    percent = min(100, int((segment.end / total_duration) * 100))
                    progress_callback(percent, f"Segment {i} işleniyor...")

            logger.info("Analiz işlemi başarıyla tamamlandı.")
            return results, info
        except Exception as e:
            logger.error(f"Analiz hatası: {str(e)}")
            raise e
        finally:
            if temp_audio and os.path.exists(temp_audio):
                try:
                    os.remove(temp_audio)
                except:
                    pass

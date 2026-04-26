import os
import sys
import json

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import ensure_directories, get_ffmpeg_path
from src.logger import logger
from src.gui import App

def main():
    # Fix for Windows Taskbar Icon
    if sys.platform == "win32":
        import ctypes
        myappid = 'pau.iibf.transcriber.v1' # unique identifier
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    logger.info("Starting PAU Local Transcription Tool...")
    ensure_directories()
    
    # Configure PATH for bundled ffmpeg
    ffmpeg_exe = get_ffmpeg_path()
    if os.path.exists(ffmpeg_exe):
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        os.environ["PATH"] += os.pathsep + ffmpeg_dir
        logger.info(f"Using bundled ffmpeg from {ffmpeg_dir}")
    else:
        logger.warning("Bundled FFmpeg not found, relying on system PATH.")

    # Load config
    config = {}
    config_path = "config.json"
    if getattr(sys, 'frozen', False):
        config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            logger.info("Config loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")

    # Start Application
    try:
        app = App(config=config)
        app.mainloop()
    except Exception as e:
        logger.critical(f"Critical application failure: {str(e)}")

if __name__ == "__main__":
    main()

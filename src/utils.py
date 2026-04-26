import os
import sys

def format_time(seconds: float) -> str:
    """Format seconds into HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_srt_time(seconds: float) -> str:
    """Format seconds into SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis == 1000:
        millis = 0
        secs += 1
        if secs == 60:
            secs = 0
            minutes += 1
            if minutes == 60:
                minutes = 0
                hours += 1
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def get_base_path() -> str:
    """Get the base path of the executable or current script."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS # When using pyinstaller, it extracts to Temp/_MEIxx
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_data_path():
    """Returns the base path for application data (models, outputs, logs)."""
    if getattr(sys, 'frozen', False):
        # Use AppData for production to ensure write permissions
        app_data = os.environ.get('APPDATA')
        if app_data:
            base_dir = os.path.join(app_data, "pau-iibf-transkript")
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            return base_dir
    return os.getcwd()

def ensure_directories():
    """Ensure required directories exist within the data directory."""
    dirs = ["models", "outputs", "logs"]
    base_dir = get_data_path()
    for d in dirs:
        dir_path = os.path.join(base_dir, d)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

def get_ffmpeg_path():
    """Returns the path to bundled ffmpeg if it exists, otherwise assumes it's in PATH."""
    # FFmpeg is bundled in the resources folder (read-only is fine for execution)
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        bundled_ffmpeg = os.path.join(exe_dir, "ffmpeg", "ffmpeg.exe")
        if os.path.exists(bundled_ffmpeg):
            return bundled_ffmpeg
    
    cwd = os.getcwd()
    bundled_ffmpeg = os.path.join(cwd, "ffmpeg", "ffmpeg.exe")
    if os.path.exists(bundled_ffmpeg):
        return bundled_ffmpeg
    return "ffmpeg"

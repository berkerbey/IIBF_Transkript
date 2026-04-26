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
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    elif any(arg.startswith("--port=") for arg in sys.argv):
        port = int([arg for arg in sys.argv if arg.startswith("--port=")][0].split("=")[1])
        
    if "--host" in sys.argv:
        host = sys.argv[sys.argv.index("--host") + 1]
    elif any(arg.startswith("--host=") for arg in sys.argv):
        host = [arg for arg in sys.argv if arg.startswith("--host=")][0].split("=")[1]

    print(f"Starting PAU Transcription Server on {host}:{port}")
    
    from src.api import app
    uvicorn.run(app, host=host, port=port, reload=False, workers=1)

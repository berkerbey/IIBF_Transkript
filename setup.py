import os
import urllib.request
import zipfile
import json

def setup_ffmpeg():
    print("Setting up FFmpeg...")
    ffmpeg_dir = "ffmpeg"
    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    # We just need windows ffmpeg binaries
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = "ffmpeg.zip"
    if not os.path.exists(os.path.join(ffmpeg_dir, "ffmpeg.exe")):
        print("Downloading FFmpeg...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # We extract to a temp folder and move
            zip_ref.extractall("ffmpeg_temp")
        
        # Move ffmpeg.exe and ffprobe.exe
        bin_dir = os.path.join("ffmpeg_temp", "ffmpeg-master-latest-win64-gpl", "bin")
        if os.path.exists(bin_dir):
            import shutil
            shutil.copy(os.path.join(bin_dir, "ffmpeg.exe"), ffmpeg_dir)
            shutil.copy(os.path.join(bin_dir, "ffprobe.exe"), ffmpeg_dir)
            
        print("Cleaning up...")
        import shutil
        shutil.rmtree("ffmpeg_temp", ignore_errors=True)
        try:
            os.remove(zip_path)
        except Exception:
            pass

def setup_logo():
    print("Setting up PAU Logo...")
    assets_dir = os.path.join("src", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    pau_logo_url = "https://upload.wikimedia.org/wikipedia/tr/6/6f/Pamukkale_University.png"
    logo_path = os.path.join(assets_dir, "pau_logo.png")
    
    if not os.path.exists(logo_path):
        try:
            req = urllib.request.Request(pau_logo_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(logo_path, 'wb') as out_file:
                out_file.write(response.read())
            
            # Try to convert to ICO using PIL if available
            try:
                from PIL import Image
                img = Image.open(logo_path)
                ico_path = os.path.join(assets_dir, "icon.ico")
                img.save(ico_path, format="ICO", sizes=[(256, 256)])
                print("Generated icon.ico")
            except ImportError:
                print("PIL not available to convert to ICO right now. We will do it later.")
        except Exception as e:
            print("Failed to download logo: ", e)

def create_config():
    config = {
        "model_name": "faster-whisper-medium",
        "device": "cpu",
        "compute_type": "int8",
         "default_language": "tr",
         "theme": "dark",
         "color_theme": "blue"
    }
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        print("Created config.json")
        
if __name__ == "__main__":
    setup_ffmpeg()
    setup_logo()
    create_config()
    print("Setup completed!")

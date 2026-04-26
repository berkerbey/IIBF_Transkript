import logging
import os
import sys

def setup_logger():
    # Determine log directory
    if getattr(sys, 'frozen', False):
        app_data = os.environ.get('APPDATA')
        if app_data:
            log_dir = os.path.join(app_data, "pau-iibf-transkript", "logs")
        else:
            log_dir = "logs"
    else:
        log_dir = "logs"

    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "app.log")
    
    logger = logging.getLogger("WhisperTranscriber")
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    # Formatting
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add handlers
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger

logger = setup_logger()

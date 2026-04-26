import sys
import os

from src.main import main

if __name__ == "__main__":
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    import multiprocessing
    multiprocessing.freeze_support()
    main()

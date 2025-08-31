# utils/logger.py
import logging
import os
from config import settings

def setup_logger():
    logger = logging.getLogger("utils.logger")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        os.makedirs(settings.logs_dir, exist_ok=True)
        handler = logging.FileHandler(settings.get_log_file_path(), encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger
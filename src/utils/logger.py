import logging
import sys
from pathlib import Path


class AppLogger:
    __slots__ = ()

    @staticmethod
    def setup(log_file: str, log_level: str) -> logging.Logger:
        logger = logging.getLogger("libvirt_manager")
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        if logger.handlers:
            return logger

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_fmt = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_fmt)

        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_fmt = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_fmt)
            logger.addHandler(file_handler)
        except OSError:
            pass

        logger.addHandler(console_handler)

        return logger

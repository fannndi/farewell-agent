import logging
import sys


def get_logger(name: str | None = None, level: int = logging.INFO) -> logging.Logger:
    """Dapatkan logger dengan StreamHandler stdout + format konsisten."""
    logger = logging.getLogger(name or __name__)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(level)

    return logger

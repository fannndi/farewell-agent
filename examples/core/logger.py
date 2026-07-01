import logging
import sys


def get_logger(name: str | None = None, level: int = logging.INFO) -> logging.Logger:
    """Dapatkan logger dengan StreamHandler stdout + format konsisten.
    Konfigurasi root logger agar semua child logger ikut terpakai.
    """
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(fmt)
        root.addHandler(handler)
        root.setLevel(level)

    logger = logging.getLogger(name or __name__)
    logger.setLevel(level)
    return logger

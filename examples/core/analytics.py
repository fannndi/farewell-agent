import logging
from statistics import median, mode, StatisticsError

log = logging.getLogger(__name__)


def rata_rata(data: list[float]) -> float:
    n = len(data)
    if n == 0:
        raise ValueError("Data kosong")
    mean = sum(data) / n
    log.debug("Mean dari %d items: %s", n, mean)
    return mean


def median_custom(data: list[float]) -> float:
    if not data:
        raise ValueError("Data kosong")
    data_sorted = sorted(data)
    m = median(data_sorted)
    log.debug("Median dari %d items: %s", len(data_sorted), m)
    return m


def modus(data: list[float]) -> float:
    if not data:
        raise ValueError("Data kosong")
    try:
        m = mode(data)
        log.debug("Modus dari %d items: %s", len(data), m)
        return m
    except StatisticsError:
        log.warning("Tidak ada modus unik dalam data")
        raise


def deskripsi(data: list[float]) -> dict:
    log.info("Deskripsi statistik untuk %d items", len(data))
    return {
        "n": len(data),
        "mean": rata_rata(data),
        "median": median_custom(data),
        "min": min(data),
        "max": max(data),
        "range": max(data) - min(data),
    }

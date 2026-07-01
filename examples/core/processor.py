import logging

log = logging.getLogger(__name__)


def transform(items: list[int], factor: int = 2) -> list[int]:
    log.info("Transform %d items with factor=%d", len(items), factor)
    result = [x * factor for x in items]
    log.debug("Result: %s", result)
    return result


def filter_positive(items: list[int]) -> list[int]:
    log.info("Filter positive from %d items", len(items))
    result = [x for x in items if x > 0]
    log.debug("Positive: %s", result)
    return result


def summarize(items: list[int]) -> dict:
    log.info("Summarize %d items", len(items))
    s = sum(items)
    n = len(items)
    avg = s / n if n else 0
    summary = {"sum": s, "count": n, "avg": avg, "max": max(items) if items else 0}
    log.info("Summary: %s", summary)
    return summary

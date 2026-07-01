"""Worker pool — combo-aware selection, scribe designation."""

import json, time
from pathlib import Path
from . import config
from .state.io import read_json, write_json

COUNTER_FILE = "worker_counter.json"
USAGE_LOG = "worker_usage.jsonl"
SCRIBE_KEYWORDS = {"memory", "context", "obsidian", "summary", "scribe", "catat", "tulis", "ringkas"}

def _counter_path() -> Path:
    return config.FAREWELL_DIR / COUNTER_FILE

def _usage_path() -> Path:
    return config.FAREWELL_DIR / USAGE_LOG

def _log_usage(model_name: str, task_class: str | None, task_hint: str):
    entry = {
        "ts": time.time(),
        "model": model_name,
        "task_class": task_class,
        "hint": (task_hint or "")[:80],
    }
    p = _usage_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def get_pool() -> list[str]:
    cfg = config.load_env()
    raw = cfg.get("WORKER", "")
    return [m.strip() for m in raw.split(",") if m.strip()]

def scribe_model() -> str | None:
    pool = get_pool()
    if not pool:
        return None
    roles = read_json(config.ROLES_FILE, {})
    idx = roles.get("worker_pool", {}).get("scribe_index", len(pool) - 1)
    return pool[idx] if 0 <= idx < len(pool) else pool[-1]

def select_worker(task_class: str | None = None, task_hint: str = "") -> str:
    pool = get_pool()
    if not pool:
        _log_usage("WORKER", task_class, task_hint)
        return "WORKER"

    roles = read_json(config.ROLES_FILE, {})
    wp = roles.get("worker_pool", {})
    scribe_idx = wp.get("scribe_index", len(pool) - 1)

    # Scrible task? Use specific scribe model directly
    combined = f"{task_class or ''} {task_hint}".lower()
    if any(kw in combined for kw in SCRIBE_KEYWORDS):
        selected = pool[scribe_idx] if 0 <= scribe_idx < len(pool) else pool[-1]
        _log_usage(selected, task_class, task_hint)
        return selected

    # Round-robin (skip scribe)
    worker_indices = [i for i in range(len(pool)) if i != scribe_idx]
    if not worker_indices:
        worker_indices = [scribe_idx]
    counter = read_json(_counter_path(), {"idx": 0})
    idx = counter.get("idx", 0)
    selected = pool[worker_indices[idx % len(worker_indices)]]
    counter["idx"] = (idx + 1) % len(worker_indices)
    write_json(_counter_path(), counter)
    _log_usage(selected, task_class, task_hint)
    return selected

def get_usage_stats() -> list[dict]:
    p = _usage_path()
    if not p.exists():
        return []
    counts: dict[str, int] = {}
    entries = []
    for line in p.read_text(encoding="utf-8").strip().splitlines():
        if not line:
            continue
        try:
            e = json.loads(line)
            entries.append(e)
            m = e.get("model", "?")
            counts[m] = counts.get(m, 0) + 1
        except json.JSONDecodeError:
            pass
    total = sum(counts.values()) or 1
    stats = [{"model": m, "count": c, "pct": round(c / total * 100)} for m, c in sorted(counts.items(), key=lambda x: -x[1])]
    return stats

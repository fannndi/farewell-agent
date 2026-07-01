"""Worker pool — combo-aware selection, scribe designation."""

from pathlib import Path
from . import config
from .state.io import read_json, write_json

COUNTER_FILE = "worker_counter.json"
SCRIBE_KEYWORDS = {"memory", "context", "obsidian", "summary", "scribe", "catat", "tulis", "ringkas"}
_COMBO_CACHE: dict[str, bool] = {}

def _counter_path() -> Path:
    return config.FAREWELL_DIR / COUNTER_FILE

def _is_combo(name: str = "WORKER") -> bool:
    if name in _COMBO_CACHE:
        return _COMBO_CACHE[name]
    try:
        import sqlite3
        db = config._9router_db()
        if db.exists():
            conn = sqlite3.connect(str(db))
            exists = conn.execute("SELECT 1 FROM combos WHERE name=?", (name,)).fetchone()
            conn.close()
            _COMBO_CACHE[name] = exists is not None
            return _COMBO_CACHE[name]
    except Exception:
        pass
    _COMBO_CACHE[name] = False
    return False

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
        return "WORKER"

    roles = read_json(config.ROLES_FILE, {})
    wp = roles.get("worker_pool", {})
    scribe_idx = wp.get("scribe_index", len(pool) - 1)

    # Scrible task? Use specific scribe model directly
    combined = f"{task_class or ''} {task_hint}".lower()
    if any(kw in combined for kw in SCRIBE_KEYWORDS):
        return pool[scribe_idx] if 0 <= scribe_idx < len(pool) else pool[-1]

    # Regular task: use WORKER combo if available (9Router traffic visibility)
    if _is_combo("WORKER"):
        return "WORKER"

    # Fallback: round-robin (no combo — farewell-agent distributes)
    worker_indices = [i for i in range(len(pool)) if i != scribe_idx]
    if not worker_indices:
        worker_indices = [scribe_idx]
    counter = read_json(_counter_path(), {"idx": 0})
    idx = counter.get("idx", 0)
    selected = pool[worker_indices[idx % len(worker_indices)]]
    counter["idx"] = (idx + 1) % len(worker_indices)
    write_json(_counter_path(), counter)
    return selected

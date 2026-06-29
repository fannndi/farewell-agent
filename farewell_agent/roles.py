import json, os
from pathlib import Path
from . import config
from .state.io import read_json

_CONFIG_CACHE = None
_COMBO_CACHE = None

def _load_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    models = {}
    f = config.ROOT_DIR / "api-key.txt"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" not in line or line.startswith("#"): continue
            k, v = line.split("=", 1)
            models[k.strip()] = v.strip()
    _CONFIG_CACHE = models
    return models

def _load_combo_names() -> set[str]:
    global _COMBO_CACHE
    if _COMBO_CACHE is not None:
        return _COMBO_CACHE
    try:
        import sqlite3
        db = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
        if db.exists():
            conn = sqlite3.connect(str(db))
            names = {row[0] for row in conn.execute("SELECT name FROM combos")}
            conn.close()
            _COMBO_CACHE = names
            return names
    except Exception: pass
    _COMBO_CACHE = set()
    return set()

def _alias(key: str, value: str, combos: set[str]) -> str:
    return key if key in combos else value

def invalidate_cache():
    global _CONFIG_CACHE, _COMBO_CACHE
    _CONFIG_CACHE = None
    _COMBO_CACHE = None

def resolve_for_tier(tier: str, task_class: str | None = None) -> dict:
    roles = read_json(config.ROLES_FILE) or {}
    tiers = roles.get("tiers", {})
    overrides = roles.get("task_overrides", {})
    tier_config = tiers.get(tier, tiers.get("tim", {}))
    cfg = _load_config()
    combos = _load_combo_names()

    if task_class and task_class in overrides:
        worker_key = overrides[task_class]
    else:
        worker_key = "worker_default"

    def _resolve(key: str) -> str:
        if key == "worker_default":
            k = tier_config.get("worker_default", "WORKER")
        elif key == "worker_pro":
            k = tier_config.get("worker_pro", "WORKER_PRO")
        else:
            k = tier_config.get(key, "SPECIAL")
        val = cfg.get(k, k.lower())
        return _alias(k, val, combos)

    return {
        "leader": _resolve("leader"),
        "special": _resolve("special"),
        "worker": _resolve(worker_key),
        "tier": tier,
        "task_class": task_class,
    }

def resolve_agent(task_class: str | None, work_mode: str) -> str:
    roles = read_json(config.ROLES_FILE) or {}
    plan_agents = roles.get("plan_agents", ["team", "planner"])
    if work_mode == "plan":
        return plan_agents[0]
    agent_map = roles.get("agent_map", {})
    return agent_map.get(task_class or "", agent_map.get("default", "build"))

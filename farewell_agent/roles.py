import json
from pathlib import Path
from . import config
from .state.io import read_json

_CONFIG_CACHE = None
_COMBO_CACHE = None

PLAN_AGENTS = {
    "default": "team",
    "audit": "architect",
    "learn": "planner",
    "research": "planner",
    "feature": "team",
    "fix": "team",
    "refactor": "team",
    "health": "build",
}

AGENT_MAP = {
    "security-review": "security-reviewer",
    "verification-loop": "tdd-guide",
    "self-heal": "build-error-resolver",
    "deploy": "senior-engineer",
    "rust-debug": "senior-engineer",
    "kotlin-debug": "senior-engineer",
    "code-review": "junior-reviewer",
    "review": "junior-reviewer",
    "architecture": "architect",
    "plan": "planner",
    "research": "docs-lookup",
    "default": "build",
}

def _load_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    _CONFIG_CACHE = config.load_env()
    return _CONFIG_CACHE

def _load_combo_names() -> set[str]:
    global _COMBO_CACHE
    if _COMBO_CACHE is not None:
        return _COMBO_CACHE
    try:
        import sqlite3
        db = config._9router_db()
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
    if work_mode == "plan":
        return PLAN_AGENTS.get(task_class or "default", "team")
    return AGENT_MAP.get(task_class or "", AGENT_MAP.get("default", "build"))

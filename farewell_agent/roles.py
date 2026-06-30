"""Model resolution — resolve model keys to roles, check org registry."""

from . import config
from .state.io import read_json

_CONFIG_CACHE = None
_COMBO_CACHE = None

PLAN_AGENTS = {
    "default": "planner",
    "audit": "architect",
    "learn": "planner",
    "research": "docs-lookup",
    "feature": "planner",
    "fix": "planner",
    "refactor": "planner",
    "health": "build",
}

AGENT_MAP = {
    "security-review":     "security-reviewer",
    "verification-loop":   "tdd-guide",
    "self-heal":           "build-error-resolver",
    "deploy":              "senior-engineer",
    "rust-debug":          "senior-engineer",
    "kotlin-debug":        "senior-engineer",
    "code-review":         "junior-reviewer",
    "review":              "junior-reviewer",
    "architecture":        "architect",
    "plan":                "planner",
    "research":            "docs-lookup",
    "default":             "build",
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
    return value

def invalidate_cache():
    global _CONFIG_CACHE, _COMBO_CACHE
    _CONFIG_CACHE = None
    _COMBO_CACHE = None

def is_org(model_key: str) -> bool:
    roles = read_json(config.ROLES_FILE) or {}
    registry = roles.get("org_registry", [])
    return model_key in registry

def resolve_model(model_key: str) -> dict:
    roles = read_json(config.ROLES_FILE) or {}
    resolve = roles.get("resolve", {})
    cfg = _load_config()
    combos = _load_combo_names()

    entry = resolve.get(model_key, {})
    role = entry.get("role", "executor")
    agent = entry.get("agent", "build")

    raw_val = cfg.get(model_key, model_key.lower())
    resolved_model = _alias(model_key, raw_val, combos)
    raw_worker = cfg.get("WORKER", "WORKER")
    worker_model = _alias("WORKER", raw_worker, combos)

    return {
        "model_key": model_key,
        "resolved": resolved_model,
        "role": role,
        "agent": agent,
        "worker": worker_model,
    }

def resolve_agent(task_class: str | None, work_mode: str, model_key: str | None = None) -> str:
    if work_mode == "plan":
        return PLAN_AGENTS.get(task_class or "default", "planner")
    if model_key and not is_org(model_key):
        return "build"
    return AGENT_MAP.get(task_class or "", AGENT_MAP.get("default", "build"))

def resolve_for_tier(tier: str, task_class: str | None = None) -> dict:
    """Deprecated — kept for sync.py compat. Maps tier to model keys."""
    roles = read_json(config.ROLES_FILE) or {}
    overrides = roles.get("task_overrides", {})
    cfg = _load_config()
    combos = _load_combo_names()

    if task_class and task_class in overrides:
        worker_key = overrides[task_class]
    else:
        worker_key = "worker_default"

    tier_map = {"divisi": "LEADER_1", "tim": "SPECIAL", "bawahan": "WORKER"}
    leader_key = tier_map.get(tier, "SPECIAL")
    special_key = "SPECIAL"
    worker_key_actual = {"worker_default": "WORKER", "worker_pro": "WORKER_PRO"}.get(worker_key, "WORKER")

    def _r(k):
        val = cfg.get(k, k.lower())
        return _alias(k, val, combos)

    return {
        "leader": _r(leader_key),
        "special": _r(special_key),
        "worker": _r(worker_key_actual),
        "tier": tier,
        "task_class": task_class or "",
    }

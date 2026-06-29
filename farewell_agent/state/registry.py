from datetime import date
from pathlib import Path
from .io import read_json, write_json
from .. import config

def load() -> dict:
    return read_json(config.REGISTRY_FILE) or {"active": "", "projects": {}}

def save(reg: dict):
    write_json(config.REGISTRY_FILE, reg)

def get_active() -> str:
    return load().get("active", "")

def get_info(name: str) -> dict | None:
    return load().get("projects", {}).get(name)

def get_code(name: str) -> str:
    info = get_info(name)
    return info.get("project_code", "???") if info else "???"

def get_path(name: str) -> str:
    info = get_info(name)
    return info.get("path", "") if info else ""

def list_all() -> list[dict]:
    reg = load()
    active = reg.get("active", "")
    result = []
    for name, info in reg.get("projects", {}).items():
        result.append({
            "code": info.get("project_code", "???"), "name": name,
            "type": info.get("type", "?"), "dominan": info.get("dominan", ""),
            "active": name == active,
            "path": info.get("path", ""),
        })
    return sorted(result, key=lambda p: p["code"])

def register(name: str, path_str: str, stack: list[str], ptype: str, dominan: str) -> dict:
    reg = load()
    path = str(Path(path_str).resolve())
    if name in reg.get("projects", {}):
        code = reg["projects"][name]["project_code"]
        action = "updated"
    else:
        code = _next_code(reg)
        reg.setdefault("projects", {})[name] = {}
        action = "registered"
    reg["projects"][name] = {
        "project_code": code, "type": ptype, "path": path,
        "last_used": date.today().isoformat(),
        "context_file": f"{name}.md", "dominan": dominan, "is_local": False,
    }
    reg["active"] = name
    save(reg)
    return {"action": action, "code": code}

def _next_code(reg: dict) -> str:
    max_n = 0
    for name, info in reg.get("projects", {}).items():
        c = info.get("project_code", "")
        if c.isdigit(): max_n = max(max_n, int(c))
    return f"{max_n + 1:03d}"

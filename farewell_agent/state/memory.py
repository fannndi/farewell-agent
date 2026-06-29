from datetime import datetime, timezone
from pathlib import Path
from .io import read_json, write_json
from .. import config

MEMORY_FILE = "memory.json"

def _project_dir(code: str, name: str) -> Path:
    d = config.MEMORY_DIR / f"{code}-{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d

def _memory_path(code: str, name: str) -> Path:
    return _project_dir(code, name) / MEMORY_FILE

def memory_content(code: str, name: str) -> str:
    p = _project_dir(code, name) / "MEMORY.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""

def save_memory(code: str, name: str, content: str, sync_obsidian: bool = True):
    max_chars = 2200
    if len(content) > max_chars:
        raise ValueError(f"Memory too long ({len(content)}/{max_chars} chars). Consolidate first.")
    p = _project_dir(code, name) / "MEMORY.md"
    p.write_text(content, encoding="utf-8")
    if sync_obsidian:
        try:
            from ..obsidian import sync_memory
            sync_memory(code, name, content, "memory")
        except Exception: pass

def user_content(code: str, name: str) -> str:
    p = _project_dir(code, name) / "USER.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""

def save_user(code: str, name: str, content: str, sync_obsidian: bool = True):
    max_chars = 1375
    if len(content) > max_chars:
        raise ValueError(f"User profile too long ({len(content)}/{max_chars} chars). Consolidate first.")
    p = _project_dir(code, name) / "USER.md"
    p.write_text(content, encoding="utf-8")
    if sync_obsidian:
        try:
            from ..obsidian import sync_memory
            sync_memory(code, name, content, "user")
        except Exception: pass

def save_session(code: str, name: str, summary: str, session_id: str | None = None, files: list[str] | None = None, msgs: int = 1):
    p = _memory_path(code, name)
    data = read_json(p) or {}
    data.update({
        "project_code": code, "project_name": name,
        "last_summary": summary, "session_id": session_id or data.get("session_id"),
        "files_touched": files or data.get("files_touched", []),
        "user_messages": data.get("user_messages", 0) + msgs,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    write_json(p, data)

def load_session(code: str, name: str) -> dict:
    return read_json(_memory_path(code, name)) or {}

def get_context(code: str, name: str) -> str:
    mem = load_session(code, name)
    if not mem: return ""
    parts = []
    if mem.get("last_summary"):
        parts.append(f"Previous session: {mem['last_summary']}")
    if mem.get("files_touched"):
        parts.append(f"Files: {', '.join(mem['files_touched'][:5])}")
    if mem.get("user_messages"):
        parts.append(f"{mem['user_messages']} message(s)")
    return " | ".join(parts)

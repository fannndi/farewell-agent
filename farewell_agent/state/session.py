"""Session continuity -- track lineage, offer resume, store full context per run."""

from datetime import datetime, timezone
from pathlib import Path
from .io import read_json, write_json
from .. import config

LINEAGE_FILE = "lineage.json"

def _lineage_path(code: str, name: str) -> Path:
    d = config.MEMORY_DIR / f"{code}-{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d / LINEAGE_FILE

def start_session(code: str, name: str, task: str, agent: str, model: str, task_class: str | None) -> str:
    """Create a new session entry. Returns session_id."""
    lineage = read_json(_lineage_path(code, name)) or {"sessions": [], "last_active": None}
    parent = lineage["sessions"][-1]["id"] if lineage["sessions"] else None
    n = len(lineage["sessions"]) + 1
    session_id = f"{code}-{name[:8]}-{n}-{datetime.now().strftime('%H%M%S')}"

    entry = {
        "id": session_id,
        "parent": parent,
        "task": task[:200],
        "agent": agent,
        "model": model,
        "task_class": task_class,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "ended_at": None,
        "status": "started",
        "opencode_session_id": None,
        "summary": None,
    }
    lineage["sessions"].append(entry)
    lineage["last_active"] = session_id
    write_json(_lineage_path(code, name), lineage)
    return session_id

def end_session(code: str, name: str, session_id: str, status: str, opencode_sid: str | None, summary: str, tokens_in: int = 0, tokens_out: int = 0):
    """Mark session as completed/failed."""
    lineage = read_json(_lineage_path(code, name))
    if not lineage: return
    for s in lineage["sessions"]:
        if s["id"] == session_id:
            s["ended_at"] = datetime.now(timezone.utc).isoformat()
            s["status"] = status
            s["opencode_session_id"] = opencode_sid or s.get("opencode_session_id")
            s["summary"] = summary[:300]
            s["tokens_in"] = tokens_in
            s["tokens_out"] = tokens_out
            break
    write_json(_lineage_path(code, name), lineage)

def last_session(code: str, name: str) -> dict | None:
    """Get the most recent session entry."""
    lineage = read_json(_lineage_path(code, name))
    if not lineage or not lineage["sessions"]: return None
    return lineage["sessions"][-1]

def recent_sessions(code: str, name: str, n: int = 5) -> list[dict]:
    """Get last N sessions."""
    lineage = read_json(_lineage_path(code, name))
    if not lineage: return []
    return lineage["sessions"][-n:]

def all_projects_recent(n_per_project: int = 3) -> list[dict]:
    """Get recent sessions across all projects."""
    mp = config.MEMORY_DIR
    if not mp.exists(): return []
    all_s = []
    for p in mp.iterdir():
        if not p.is_dir(): continue
        lf = p / LINEAGE_FILE
        if not lf.exists(): continue
        data = read_json(lf)
        if data and data["sessions"]:
            for s in data["sessions"][-n_per_project:]:
                s["project"] = p.name
                all_s.append(s)
    return sorted(all_s, key=lambda x: x.get("started_at", ""), reverse=True)[:10]

def suggest_resume(code: str, name: str) -> str | None:
    """Return prompt text if there's an interrupted session."""
    last = last_session(code, name)
    if not last: return None
    if last["status"] == "completed":
        return f"Last session: {last.get('summary', last['task'])[:100]}"
    if last["status"] in ("started", "failed"):
        return f"[Resume?] Previous session incomplete: {last['task'][:80]} (status: {last['status']})"
    return None

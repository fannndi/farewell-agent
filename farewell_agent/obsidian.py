"""Obsidian vault integration — sync MEMORY.md/USER.md + session notes to vault."""

from datetime import datetime
from pathlib import Path
from . import config

def _vault_path() -> Path | None:
    """Read OBSIDIAN_VAULT from api-key.txt."""
    key_file = config.ROOT_DIR / "api-key.txt"
    if not key_file.exists(): return None
    for line in key_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("OBSIDIAN_VAULT="):
            p = Path(line.split("=", 1)[1].strip())
            if p.exists(): return p
    return None

def is_configured() -> bool:
    return _vault_path() is not None

def vault_path() -> str:
    p = _vault_path()
    return str(p) if p else ""

def sync_memory(code: str, name: str, content: str, target: str = "memory"):
    """Write MEMORY.md or USER.md to Obsidian vault."""
    vault = _vault_path()
    if not vault: return False
    project_dir = vault / f"{code}-{name}"
    project_dir.mkdir(parents=True, exist_ok=True)
    fname = "MEMORY.md" if target == "memory" else "USER.md"
    (project_dir / fname).write_text(content, encoding="utf-8")
    return True

def write_session_note(code: str, name: str, task: str, agent: str, model: str, success: bool, summary: str):
    """Append a session note to Obsidian vault."""
    vault = _vault_path()
    if not vault: return False
    project_dir = vault / f"{code}-{name}"
    project_dir.mkdir(parents=True, exist_ok=True)
    note_file = project_dir / "Session-Log.md"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    status = "✅" if success else "❌"
    line = f"- {status} **{ts}** — {task[:100]} → `{agent} @ {model}`\n"
    if summary:
        line += f"  _{summary[:200]}_\n"
    with open(str(note_file), "a", encoding="utf-8") as f:
        f.write(line)
    return True

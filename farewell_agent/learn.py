"""Learning loop — analyze task results, suggest memory updates, detect patterns."""

from datetime import datetime, timezone
from pathlib import Path
from . import config
from .state.io import read_json, write_json
from .state.memory import save_memory, memory_content

PATTERNS_FILE = "patterns.json"

def _patterns_path(code: str, name: str) -> Path:
    d = config.MEMORY_DIR / f"{code}-{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d / PATTERNS_FILE

def analyze_completion(code: str, name: str, task: str, task_class: str | None, agent: str,
                        success: bool, duration_s: float, summary: str,
                        footer_ok: bool = False, raw_input: str = "", enriched_input: str = ""):
    """After a task completes, analyze and suggest memory updates."""
    # 1. Track pattern
    patterns = read_json(_patterns_path(code, name)) or {
        "total": 0, "success": 0, "failed": 0,
        "by_class": {}, "by_agent": {},
        "footer_ok": 0, "last_analysis": None,
    }
    patterns["total"] += 1
    if success:
        patterns["success"] += 1
    else:
        patterns["failed"] += 1
    if footer_ok:
        patterns["footer_ok"] = patterns.get("footer_ok", 0) + 1

    cls = task_class or "default"
    patterns.setdefault("by_class", {}).setdefault(cls, {"total": 0, "success": 0})
    patterns["by_class"][cls]["total"] += 1
    if success:
        patterns["by_class"][cls]["success"] += 1

    patterns.setdefault("by_class_footer", {}).setdefault(cls, 0)
    if footer_ok:
        patterns["by_class_footer"][cls] = patterns["by_class_footer"].get(cls, 0) + 1

    patterns.setdefault("by_agent", {}).setdefault(agent, {"total": 0, "success": 0})
    patterns["by_agent"][agent]["total"] += 1
    if success:
        patterns["by_agent"][agent]["success"] += 1

    patterns["last_analysis"] = datetime.now(timezone.utc).isoformat()
    patterns["last_raw_input"] = raw_input[:200] if raw_input else task[:200]
    patterns["last_enriched"] = enriched_input[:200] if enriched_input else ""
    write_json(_patterns_path(code, name), patterns)

    # 2. Suggest MEMORY.md updates based on task
    suggestions = _generate_suggestions(code, name, task, task_class, success, patterns)

    # Auto-consolidate memory every 5 successful tasks
    if success and patterns["total"] > 0 and patterns["total"] % 5 == 0:
        _auto_consolidate(code, name, patterns)

    # Auto-evolve every 10 tasks
    if patterns["total"] > 0 and patterns["total"] % 10 == 0:
        try:
            from .evolve import run as evolve_run
            evo_changes = evolve_run(code, name)
            for c in evo_changes:
                suggestions.append(f"[Evolve] {c}")
        except Exception as e:
            suggestions.append(f"[Evolve] skipped: {e}")

    return suggestions


def _auto_consolidate(code: str, name: str, patterns: dict):
    """Write a compact memory summary based on task patterns."""
    by_class = patterns.get("by_class", {})
    lines = [f"Task history ({patterns['total']} total, {patterns['success']}/{patterns['failed']} success/fail):"]
    for cls, stats in sorted(by_class.items()):
        lines.append(f"- {cls}: {stats['success']}/{stats['total']} success")
    content = "\n".join(lines) + "\n"
    try:
        current = memory_content(code, name)
        if content not in current:
            new_mem = current + "\n" + content if current else content
            save_memory(code, name, new_mem)
    except ValueError:
        pass


def _generate_suggestions(code: str, name: str, task: str, task_class: str | None,
                           success: bool, patterns: dict) -> list[str]:
    """Generate natural language suggestions for memory updates."""
    suggestions = []
    current_mem = memory_content(code, name)

    workflow_keywords = {
        "deploy": None,
        "build": None,
        "test": None,
        "docker": None,
        "migration": None,
    }
    task_lower = task.lower()
    for kw in workflow_keywords:
        if kw in task_lower and kw not in current_mem.lower():
            suggestions.append(f"Task involved '{kw}' — consider saving steps to MEMORY.md.")
            break

    if task_class and task_class in patterns.get("by_class", {}):
        stats = patterns["by_class"][task_class]
        if stats["total"] >= 3:
            rate = stats["success"] / stats["total"]
            if rate < 0.5:
                suggestions.append(
                    f"Low success rate ({rate:.0%}) for '{task_class}' "
                    f"({stats['success']}/{stats['total']}). Consider switching model tier."
                )

    if task_class and task_class not in current_mem.lower():
        suggestions.append(f"First '{task_class}' task — note any project-specific workflow to MEMORY.md.")

    return suggestions


def insights(code: str, name: str) -> str:
    """Return a one-line insight about task patterns."""
    patterns = read_json(_patterns_path(code, name))
    if not patterns or patterns["total"] == 0:
        return ""

    rate = patterns["success"] / patterns["total"] * 100 if patterns["total"] > 0 else 0
    parts = [f"{patterns['total']} tasks run ({rate:.0f}% success)"]

    # Worst performer
    if patterns.get("by_class"):
        worst = min(patterns["by_class"].items(),
                    key=lambda x: x[1]["success"] / x[1]["total"] if x[1]["total"] > 0 else 1)
        if worst[1]["total"] >= 2 and worst[1]["success"] / worst[1]["total"] < 0.5:
            parts.append(f"weakest: {worst[0]} ({worst[1]['success']}/{worst[1]['total']})")

    return " | ".join(parts)

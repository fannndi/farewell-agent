"""Self-evolution engine — analyzes patterns, tunes prompt/model, writes lessons."""

from .state.io import read_json, write_json
from .state.memory import save_memory, memory_content
from .learn import _patterns_path

EVOLVE_FILE = "evolve.json"


def _evolve_path(code: str, name: str):
    from . import config
    d = config.MEMORY_DIR / f"{code}-{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d / EVOLVE_FILE


def run(code: str, name: str) -> list[str]:
    """Run evolution analysis for a project. Returns list of actions taken."""
    changes = []
    patterns = read_json(_patterns_path(code, name))
    if not patterns or patterns.get("total", 0) < 5:
        return ["Not enough data (need 5+ tasks)"]

    footer_ok = patterns.get("footer_ok", 0)
    total = patterns.get("total", 1)
    footer_rate = footer_ok / total

    evolve_data = read_json(_evolve_path(code, name)) or {
        "evolutions": 0, "last_footer_rate": 1.0, "history": []
    }

    # 1. Check footer rate
    if footer_rate < 0.95:
        _record_evolution(evolve_data, "footer_rate", f"{footer_rate:.0%}")
        lesson = f"- evolved: footer rate {footer_rate:.0%} — escalate prompt instruction"
        changes.append(lesson)

    # 2. Check per-class success rate
    by_class = patterns.get("by_class", {})
    for cls, stats in by_class.items():
        if stats["total"] >= 3:
            rate = stats["success"] / stats["total"]
            if rate < 0.5:
                _record_evolution(evolve_data, f"class:{cls}", f"{rate:.0%} success")
                lesson = f"- evolved: low success {cls} ({rate:.0%}) — consider model tier upgrade"
                changes.append(lesson)

    # 3. Write lessons to MEMORY.md
    if changes:
        current = memory_content(code, name)
        new_entry = f"\n## Evolution ({_now()})\n" + "\n".join(changes)
        if new_entry not in current:
            consolidated = current + new_entry if current else new_entry
            if len(consolidated) <= 2100:
                save_memory(code, name, consolidated)
            else:
                save_memory(code, name, current[:1800] + f"\n## Evolution ({_now()})\nevolved: consolidated memory\n")

    evolve_data["last_footer_rate"] = footer_rate
    evolve_data["evolutions"] += len(changes)
    write_json(_evolve_path(code, name), evolve_data)

    return changes if changes else ["All metrics healthy — no evolution needed"]


def _record_evolution(data: dict, metric: str, value: str):
    data.setdefault("history", []).append({"metric": metric, "value": value, "at": _now()})


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")


def should_evolve(code: str, name: str) -> bool:
    """Check if evolution should run (every 10 tasks)."""
    patterns = read_json(_patterns_path(code, name))
    if not patterns:
        return False
    total = patterns.get("total", 0)
    return total > 0 and total % 10 == 0

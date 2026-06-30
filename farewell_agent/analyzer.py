"""Model performance analyzer - queries evodb, suggests optimizations."""

from . import config, evodb
from .state.io import read_json, write_json
from .helpers import info

SUGGESTION_THRESHOLD = 0.1  # min improvement rate to suggest swap


def analyze(project: str | None = None) -> list[dict]:
    best = evodb.best_model_per_task_class(project)
    footer = evodb.footer_rate(project)
    suggestions = []

    if footer < 0.95:
        suggestions.append({
            "type": "footer",
            "priority": "high",
            "message": f"Footer rate {footer:.0%} - perlu prompt reinforcement",
        })

    for cls, data in best.items():
        suggestions.append({
            "type": "model_preference",
            "priority": "medium",
            "task_class": cls,
            "model": data["model"],
            "rate": data["rate"],
            "total": data["total"],
            "avg_duration": data["avg_duration"],
            "message": f"{cls} -> {data['model']} ({data['rate']:.0%} sukses, {data['total']} tasks)",
        })

    return suggestions


def auto_tune(project: str | None = None) -> list[str]:
    roles = read_json(config.ROLES_FILE) or {}
    if not roles.get("auto_tune", False):
        return ["auto_tune disabled in roles.json"]

    prefs = roles.get("task_model_preferences", {})
    best = evodb.best_model_per_task_class(project)
    changes = []

    for cls, data in best.items():
        current = prefs.get(cls, {}).get("model")
        if current == data["model"]:
            continue
        if current and data["rate"] < 0.5:
            continue
        if current:
            changes.append(f"Swap {cls}: {current} -> {data['model']} ({data['rate']:.0%})")
        else:
            changes.append(f"Set {cls}: -> {data['model']} ({data['rate']:.0%})")
        prefs[cls] = {"model": data["model"],
                      "reason": f"{data['rate']:.0%} success from {data['total']} tasks"}

    if changes:
        roles["task_model_preferences"] = prefs
        write_json(config.ROLES_FILE, roles)
        for c in changes:
            evodb.record_evolution("model_preference", current or "", data["model"])

    return changes if changes else ["No model preference changes needed"]


def report(project: str | None = None) -> str:
    lines = ["\n  === Model Performance ==="]
    perf = evodb.model_performance(project)
    for p in perf:
        rate = p["successes"] / p["total"] * 100 if p["total"] else 0
        footer = p["footers"] / p["total"] * 100 if p["total"] else 0
        lines.append(f"  {p['model']:<35} {p['task_class'] or 'default':<15} "
                     f"{p['total']:>3} tasks  {rate:>3.0f}% ok  {footer:>3.0f}% footer  {p['avg_duration']:>5.1f}s")
    footer_rate = evodb.footer_rate(project)
    lines.append(f"\n  Overall footer rate: {footer_rate:.0%}")
    evos = evodb.recent_evolutions(3)
    if evos:
        lines.append("\n  Recent evolutions:")
        for e in evos:
            lines.append(f"    {e['applied_at'][:16]} -- {e['metric']}: {e['old_value']} -> {e['new_value']}")
    return "\n".join(lines)




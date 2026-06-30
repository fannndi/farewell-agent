"""Token cost tracking + execution trace logging (Hermes Self-Evolution pattern)."""

from datetime import datetime, timezone
from . import config
from .state.io import read_json, write_json

TRACE_HEADER = "timestamp,project,task_class,agent,model,success,summary,duration_s"

def log_entry(project: str, model: str, tokens_in: int, tokens_out: int, cost: float):
    header = "timestamp,project,model,tokens_in,tokens_out,cost"
    line = f"{datetime.now(timezone.utc).isoformat()},{project},{model},{tokens_in},{tokens_out},{cost:.6f}"
    config.COST_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not config.COST_LOG.exists():
        config.COST_LOG.write_text(header + "\n", encoding="utf-8")
    with open(str(config.COST_LOG), "a", encoding="utf-8") as f:
        f.write(line + "\n")

def write_trace(project: str, task_class: str | None, agent: str, model: str, success: bool, summary: str, duration_s: float):
    """Execution trace -- Hermes Self-Evolution pattern. Append to trace log."""
    trace_file = config.FAREWELL_DIR / "trace-log.csv"
    trace_file.parent.mkdir(parents=True, exist_ok=True)
    if not trace_file.exists():
        trace_file.write_text(TRACE_HEADER + "\n", encoding="utf-8")
    esc_summary = summary.replace('"', '""')
    line = (
        f"{datetime.now(timezone.utc).isoformat()},"
        f"{project},{task_class or 'default'},{agent},{model},"
        f"{'1' if success else '0'},\"{esc_summary}\",{duration_s:.1f}"
    )
    with open(str(trace_file), "a", encoding="utf-8") as f:
        f.write(line + "\n")

def budget_status() -> dict:
    budget = read_json(config.COST_BUDGET) or {"daily": 5.0, "monthly": 50.0}
    spent = _total_spent_today()
    return {
        "daily_budget": budget.get("daily", 5.0),
        "monthly_budget": budget.get("monthly", 50.0),
        "spent_today": spent["today"],
        "spent_month": spent["month"],
    }

def recent_traces(n: int = 5) -> list[dict]:
    """Last N execution traces for context footer."""
    trace_file = config.FAREWELL_DIR / "trace-log.csv"
    if not trace_file.exists(): return []
    lines = trace_file.read_text(encoding="utf-8").strip().splitlines()
    if len(lines) <= 1: return []
    result = []
    for line in lines[-n:]:
        parts = line.split(",")
        if len(parts) >= 7:
            result.append({
                "ts": parts[0], "project": parts[1],
                "class": parts[2], "agent": parts[3],
                "success": parts[5] == "1",
                "summary": parts[6].strip('"'),
            })
    return result

def _total_spent_today() -> dict:
    if not config.COST_LOG.exists():
        return {"today": 0.0, "month": 0.0}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    spent_today = 0.0
    spent_month = 0.0
    for line in config.COST_LOG.read_text(encoding="utf-8").splitlines()[1:]:
        if not line.strip(): continue
        parts = line.split(",")
        if len(parts) >= 6:
            ts, cost_str = parts[0], parts[5]
            try:
                cost = float(cost_str)
                if ts.startswith(today): spent_today += cost
                if ts.startswith(month): spent_month += cost
            except: pass
    return {"today": spent_today, "month": spent_month}

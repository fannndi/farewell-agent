from datetime import datetime, timezone
from . import config
from .state.io import read_json, write_json

def log_entry(project: str, model: str, tokens_in: int, tokens_out: int, cost: float):
    """Append one usage record to cost-log.csv."""
    header = "timestamp,project,model,tokens_in,tokens_out,cost"
    line = f"{datetime.now(timezone.utc).isoformat()},{project},{model},{tokens_in},{tokens_out},{cost:.6f}"
    config.COST_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not config.COST_LOG.exists():
        config.COST_LOG.write_text(header + "\n", encoding="utf-8")
    with open(str(config.COST_LOG), "a", encoding="utf-8") as f:
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

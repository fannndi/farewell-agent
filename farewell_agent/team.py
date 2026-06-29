import json
from . import config
from .state.io import write_json, read_json
from .helpers import c
from .sync import render as render_config

TIERS = {"divisi": "ON", "tim": "TIM", "bawahan": "BAWAHAN"}
LABELS = {"ON": "Divisi", "TIM": "Tim", "BAWAHAN": "Bawahan"}

def switch(tier: str):
    key = TIERS.get(tier)
    if not key:
        return status()
    write_json(config.FAREWELL_DIR / "team.json", {"team": key})
    render_config()
    from .cli import write_context_footer
    write_context_footer()
    from .roles import resolve_for_tier
    r = resolve_for_tier(tier)
    print(f"\n  {c(f'[{tier.upper()}]', 'green')} leader={c(r['leader'], 'cyan')} special={c(r['special'], 'cyan')} worker={c(r['worker'], 'cyan')}\n")

def status():
    team = _current()
    label = LABELS.get(team, "Tim")
    from .roles import resolve_for_tier
    tier_name = {"ON": "divisi", "TIM": "tim", "BAWAHAN": "bawahan"}.get(team, "tim")
    r = resolve_for_tier(tier_name)
    print(f"\n  Team: {team} ({label})")
    print(f"  Leader: {c(r['leader'], 'cyan')} | Special: {c(r['special'], 'cyan')} | Worker: {c(r['worker'], 'cyan')}\n")

def _current() -> str:
    f = config.FAREWELL_DIR / "team.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8")).get("team", "TIM")
    return "TIM"

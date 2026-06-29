from datetime import datetime, timezone
from . import config
from .state.io import read_json, write_json
from .helpers import ok, info

def switch(action: str):
    current = read_json(config.WORK_MODE_FILE, {}).get("mode", "build")
    if action == "status":
        print(f"\n  Mode: {current.upper()}\n")
        return
    if action == current:
        info(f"Already in {action.upper()}")
        return
    write_json(config.WORK_MODE_FILE, {
        "mode": action,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z"),
    })
    from .sync import render as render_config
    render_config()
    from .cli import write_context_footer
    write_context_footer()
    ok(f"Work mode set to {action.upper()}")

def current() -> str:
    return read_json(config.WORK_MODE_FILE, {}).get("mode", "build")

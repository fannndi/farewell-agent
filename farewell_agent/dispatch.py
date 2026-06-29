import json, shutil, subprocess, sys
from pathlib import Path
from . import config
from .state.registry import get_active, get_code, get_path
from .state.memory import save_session, get_context, load_session
from .roles import resolve_for_tier, resolve_agent
from .intent import classify
from .workmode import current as current_mode
from .sync import render as render_config
from .team import _current as current_team
from .helpers import ok, info, fail

def run(task: str):
    # 1. Check binary
    opencode_path = shutil.which("opencode")
    if not opencode_path:
        fail("`opencode` not found in PATH. Install OpenCode first: https://opencode.ai")
        sys.exit(1)

    # 2. Determine project
    active = get_active()
    if not active:
        fail("No active project. Run `setup-project` or `project switch` first.")
        return
    code = get_code(active)
    project_path = get_path(active)

    # 3. Classify intent
    task_class = classify(task)
    if task_class:
        info(f"Inten: {task_class}")

    # 4. Resolve model + agent
    work_mode = current_mode()
    agent = resolve_agent(task_class, work_mode)
    tier_name = {"ON": "divisi", "TIM": "tim", "BAWAHAN": "bawahan"}.get(current_team(), "tim")
    resolved = resolve_for_tier(tier_name, task_class)

    # 5. Plan mode guard
    plan_agents = ["team", "planner", "docs-lookup", "architect"]
    if work_mode == "plan" and agent not in plan_agents:
        fail(f"Task '{task_class or 'default'}' needs build mode — you're in PLAN.")
        info(f"Run `farewell-agent workmode build` first, or use plan agent directly.")
        return

    # 6. Regenerate config if needed
    render_config()
    ok(f"Config synced ({agent} @ {resolved['leader']})")

    # 7. Get or reuse session
    mem = load_session(code, active)
    session_id = mem.get("session_id") if mem else None
    session_args = []
    if session_id:
        session_args = ["--continue"]
        info(f"Reusing session {session_id[:12]}...")
    else:
        info("Starting new session")

    # 8. Build opencode command
    model_str = f"9router/{resolved['leader']}"
    cmd = [
        opencode_path, "run", task,
        "--agent", agent,
        "--model", model_str,
        "--format", "json",
    ]
    if project_path:
        cmd += ["--dir", project_path]
    if session_args:
        cmd += session_args
    cmd += ["--title", f"farewell-agent: {task[:60]}"]

    info(f"Exec: opencode run --agent {agent} --model {model_str}")
    info(f"Dir: {project_path or config.ROOT_DIR}")

    # 9. Execute
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            fail(f"OpenCode failed: {result.stderr[:500]}")
            return

        # Parse JSON response
        try:
            response = json.loads(result.stdout)
            new_session_id = response.get("session_id") or response.get("session", {}).get("id")
        except json.JSONDecodeError:
            new_session_id = None
            print(result.stdout[:1000])

        # 10. Save session
        summary = f"Ran task: {task[:80]}"
        save_session(code, active, summary, session_id=new_session_id, msgs=1)
        ok(f"Session saved ({new_session_id[:16] if new_session_id else 'no id'}...)")

        # Update context footer
        from .cli import write_context_footer
        write_context_footer()

    except subprocess.TimeoutExpired:
        fail("OpenCode timed out after 600s")
    except Exception as e:
        fail(f"Dispatch error: {e}")

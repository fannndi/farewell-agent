import json, shutil, subprocess, sys, time
from . import config
from .state.registry import get_active, get_code, get_path
from .state.memory import save_session, load_session
from .roles import resolve_for_tier, resolve_agent
from .intent import classify
from .workmode import current as current_mode
from .sync import render as render_config
from .team import _current as current_team
from .helpers import ok, info, fail
from .cost import write_trace
from . import obsidian

def run(task: str):
    t0 = time.time()
    opencode_path = shutil.which("opencode")
    if not opencode_path:
        fail("`opencode` not found in PATH. Install OpenCode first: https://opencode.ai")
        sys.exit(1)

    active = get_active()
    if not active:
        fail("No active project. Run `setup-project` or `project switch` first.")
        return
    code = get_code(active)
    project_path = get_path(active)

    task_class = classify(task)
    if task_class:
        info(f"Intent: {task_class}")

    work_mode = current_mode()
    agent = resolve_agent(task_class, work_mode)
    tier_name = {"ON": "divisi", "TIM": "tim", "BAWAHAN": "bawahan"}.get(current_team(), "tim")
    resolved = resolve_for_tier(tier_name, task_class)

    plan_agents = ["team", "planner", "docs-lookup", "architect"]
    if work_mode == "plan" and agent not in plan_agents:
        fail(f"Task '{task_class or 'default'}' needs build mode — you're in PLAN.")
        info("Run `farewell-agent workmode build` first, or use plan agent directly.")
        write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], False, "Blocked by plan mode", time.time() - t0)
        return

    render_config()
    ok(f"Config synced ({agent} @ {resolved['leader']})")

    mem = load_session(code, active)
    session_id = mem.get("session_id") if mem else None
    session_args = session_id if session_id else ["--continue"] if mem else None
    # Actually: use --continue for reusing session
    cmd_args = []
    if session_id:
        cmd_args = ["--continue"]
        info(f"Reusing session {session_id[:12]}...")
    else:
        info("Starting new session")

    model_str = f"9router/{resolved['leader']}"
    cmd = [
        opencode_path, "run", task,
        "--agent", agent,
        "--model", model_str,
        "--format", "json",
    ]
    if project_path:
        cmd += ["--dir", project_path]
    if cmd_args:
        cmd += cmd_args
    cmd += ["--title", f"farewell-agent: {task[:60]}"]

    info(f"Exec: opencode run --agent {agent} --model {model_str}")
    info(f"Dir: {project_path or config.ROOT_DIR}")

    duration = time.time() - t0
    success = False
    new_session_id = None
    summary = f"Ran: {task[:80]}"

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        duration = time.time() - t0
        if result.returncode != 0:
            fail(f"OpenCode failed: {result.stderr[:500]}")
            write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], False, f"Failed: {result.stderr[:100]}", duration)
            return

        try:
            response = json.loads(result.stdout)
            new_session_id = response.get("session_id") or response.get("session", {}).get("id")
        except json.JSONDecodeError:
            new_session_id = None
            print(result.stdout[:1000])

        success = True
        save_session(code, active, summary, session_id=new_session_id, msgs=1)
        ok(f"Session saved ({new_session_id[:16] if new_session_id else 'no id'}...)")

        # Execution trace (Hermes Self-Evolution pattern)
        write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], success, summary, duration)

        # Obsidian session note
        if obsidian.is_configured():
            obsidian.write_session_note(code, active, task, agent, resolved["leader"], success, summary)

        from .cli import write_context_footer
        write_context_footer()

    except subprocess.TimeoutExpired:
        duration = time.time() - t0
        write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], False, "Timed out (600s)", duration)
        fail("OpenCode timed out after 600s")
    except Exception as e:
        duration = time.time() - t0
        write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], False, f"Error: {str(e)[:100]}", duration)
        fail(f"Dispatch error: {e}")

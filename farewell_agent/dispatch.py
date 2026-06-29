"""Enhanced dispatch — session continuity + context enrichment + learning loop."""

import json, shutil, subprocess, sys, time
from . import config
from .state.registry import get_active, get_code, get_path
from .state.memory import save_session, load_session
from .state.session import start_session, end_session, suggest_resume
from .roles import resolve_for_tier, resolve_agent
from .intent import classify
from .context import lookup, is_ready
from .learn import analyze_completion, insights
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

    # --- 1. Intent classification (workflow + task) ---
    wf, task_class = classify(task)
    if wf:
        # High-level workflow detected — delegate to workflow orchestrator
        info(f"Workflow: {wf}")
        from .workflow import run_workflow
        run_workflow(wf, task)
        return
    if task_class:
        info(f"Intent: {task_class}")

    # --- 2. Model + agent resolution ---
    work_mode = current_mode()
    agent = resolve_agent(task_class, work_mode)
    tier_name = "tim"
    team_val = current_team()
    for k, v in {"ON": "divisi", "TIM": "tim", "BAWAHAN": "bawahan"}.items():
        if team_val == k:
            tier_name = v
            break
    resolved = resolve_for_tier(tier_name, task_class)

    # --- 3. Plan mode guard ---
    plan_agents = ["team", "planner", "docs-lookup", "architect"]
    if work_mode == "plan" and agent not in plan_agents:
        fail(f"Task '{task_class or 'default'}' needs build mode — you're in PLAN.")
        info("Run `farewell-agent workmode build` first.")
        write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], False, "Blocked by plan mode", time.time() - t0)
        return

    # --- 4. Config sync ---
    render_config()
    ok(f"Config synced ({agent} @ {resolved['leader']})")

    # --- 5. Session management ---
    resume_note = suggest_resume(code, active)
    if resume_note:
        info(resume_note)

    session_id = start_session(code, active, task, agent, resolved["leader"], task_class)
    info(f"Session: {session_id}")

    # --- 6. Buku Panduan (always consult guide book before action) ---
    print("\n  [?] Membuka buku panduan...")
    guide_block = lookup(task)
    if guide_block:
        print(guide_block[:1200])
        enriched_task = f"{task}\n\n{guide_block}"
    else:
        if is_ready():
            print("  (tidak ada artikel yang cocok di buku panduan)")
        else:
            print("  (buku panduan/Obsidian belum dikonfigurasi)")
        enriched_task = task

    # --- 7. Build command ---
    session_args = []
    mem = load_session(code, active)
    if mem and mem.get("session_id"):
        session_args = ["--continue"]
        info(f"Continuing OpenCode session {mem['session_id'][:12]}...")

    model_str = f"9router/{resolved['leader']}"
    cmd = [
        opencode_path, "run", enriched_task,
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

    # --- 8. Execute ---
    duration = time.time() - t0
    success = False
    new_session_id = None
    summary = f"Ran: {task[:80]}"

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        duration = time.time() - t0

        if result.returncode != 0:
            fail(f"OpenCode failed: {result.stderr[:300]}")
            end_session(code, active, session_id, "failed", None, f"Failed: {result.stderr[:100]}")
            write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], False, f"Failed: {result.stderr[:100]}", duration)
            return

        try:
            response = json.loads(result.stdout)
            new_session_id = response.get("session_id") or response.get("session", {}).get("id")
        except json.JSONDecodeError:
            new_session_id = None

        success = True
        save_session(code, active, summary, session_id=new_session_id, msgs=1)
        end_session(code, active, session_id, "completed", new_session_id, summary)
        ok(f"Done ({duration:.0f}s)")

        # --- 9. Execution trace ---
        write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], success, summary, duration)

        # --- 10. Obsidian note ---
        if obsidian.is_configured():
            obsidian.write_session_note(code, active, task, agent, resolved["leader"], success, summary)

        # --- 11. Learning loop ---
        suggestions = analyze_completion(code, active, task, task_class, agent, success, duration, summary)
        if suggestions:
            print(f"\n  [Learning]:")
            for s in suggestions[:2]:
                info(s)

        # --- 12. Context footer ---
        from .cli import write_context_footer
        write_context_footer()

    except subprocess.TimeoutExpired:
        duration = time.time() - t0
        end_session(code, active, session_id, "timeout", None, "Timed out (600s)")
        write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], False, "Timed out", duration)
        fail("OpenCode timed out after 600s")
    except Exception as e:
        duration = time.time() - t0
        end_session(code, active, session_id, "error", None, f"Error: {str(e)[:100]}")
        write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], False, f"Error: {str(e)[:100]}", duration)
        fail(f"Dispatch error: {e}")

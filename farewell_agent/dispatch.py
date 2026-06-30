"""Enhanced dispatch -- session continuity + context enrichment + learning loop."""

import json, shutil, subprocess, socket, sys, time
from pathlib import Path
from . import config
from .state.registry import get_active, get_code, get_path
from .state.memory import save_session, load_session, save_memory, memory_content
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
from .interpreter import refine, ensure_footer
from . import evodb

def verify_router() -> bool:
    """Check if 9Router port 20128 is reachable."""
    try:
        with socket.create_connection(("127.0.0.1", 20128), timeout=3):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def run(task: str):
    t0 = time.time()
    if not verify_router():
        info("9Router not running -- starting automatically...")
        from .daily import _ensure_9router
        if not _ensure_9router():
            fail("9Router failed to start.")
            sys.exit(1)
        ok("9Router started")

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
        # High-level workflow detected -- delegate to workflow orchestrator
        info(f"Workflow: {wf}")
        from .workflow import run_workflow
        run_workflow(wf, task)
        return
    if task_class:
        info(f"Intent: {task_class}")

    # --- 2. Model + agent resolution ---
    work_mode = current_mode()
    team_val = current_team()
    tier_name = {"ON": "divisi", "TIM": "tim", "BAWAHAN": "bawahan"}.get(team_val, "tim")
    # Resolve agent dengan konteks tier
    agent = resolve_agent(task_class, work_mode)
    resolved = resolve_for_tier(tier_name, task_class)

    # --- 3. Plan mode guard ---
    plan_agents = ["team", "planner", "docs-lookup", "architect"]
    if work_mode == "plan" and agent not in plan_agents:
        fail(f"Task '{task_class or 'default'}' needs build mode -- you're in PLAN.")
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
    else:
        if is_ready():
            print("  (tidak ada artikel yang cocok di buku panduan)")
        else:
            print("  (buku panduan/Obsidian belum dikonfigurasi)")
    enriched_task = refine(task, code, active, guide_block)
    task_class_label = task_class or "default"
    enriched_task += f"""

---

### FOOTER (WAJIB)
**Project:** {code}-{active}
**Agent:** {agent}
**Task Class:** {task_class_label}
**Next:** sarankan 1 tindakan lanjutan yang sesuai dengan konteks tugas ini

WAJIB: Cantumkan ### FOOTER di AKHIR setiap respons. Jika tidak ada FOOTER, respons dianggap TIDAK LENGKAP."""

    # --- 7. Build command ---
    session_args = []
    mem = load_session(code, active)
    if mem and mem.get("session_id"):
        session_args = ["--continue"]
        info(f"Continuing OpenCode session {mem['session_id'][:12]}...")

    model_for_task = resolved.get("preferred") or resolved["leader"]
    model_str = f"9router/{model_for_task}"
    if resolved.get("preferred_reason"):
        info(f"Model tuned: {model_for_task} ({resolved['preferred_reason']})")

    # Build command -- platform aware
    title_safe = task[:60].replace('"', "'").replace("\n", " ")
    parts = [opencode_path, "run", enriched_task, "--agent", agent, "--model", model_str, "--format", "json", "--title", title_safe]
    if project_path and str(config.ROOT_DIR.resolve()) != str(Path(project_path).resolve()):
        parts += ["--dir", str(project_path)]
    if session_args:
        parts += session_args

    if config.is_windows():
        # opencode.CMD needs cmd.exe context
        quoted = [f'"{p}"' if " " in p or '"' in p else p for p in parts]
        cmd_str = " ".join(quoted)
    else:
        cmd_str = parts  # list-arg, no shell=True

    info(f"Exec: opencode run --agent {agent} --model {model_str}")

    # --- 8. Execute ---
    duration = time.time() - t0
    success = False
    new_session_id = None
    summary = f"Ran: {task[:80]}"

    try:
        if config.is_windows():
            result = subprocess.run(cmd_str, capture_output=True, timeout=600, shell=True)
        else:
            result = subprocess.run(cmd_str, capture_output=True, timeout=600)
        duration = time.time() - t0
        out_text = result.stdout.decode("utf-8", errors="replace")
        err_text = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""

        if result.returncode != 0:
            evodb.init()
            evodb.insert_task(f"{code}-{active}", task_class, agent, resolved["leader"],
                             footer_ok=False, duration_s=duration, success=False)
            fail(f"OpenCode failed: {err_text[:300]}")
            end_session(code, active, session_id, "failed", None, f"Failed: {err_text[:100]}")
            write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], False, f"Failed: {err_text[:100]}", duration)
            return

        try:
            response = json.loads(out_text)
            new_session_id = response.get("session_id") or response.get("session", {}).get("id")
        except json.JSONDecodeError:
            new_session_id = None

        success = True
        save_session(code, active, summary, session_id=new_session_id, msgs=1)
        end_session(code, active, session_id, "completed", new_session_id, summary)
        ok(f"Done ({duration:.0f}s)")

        # --- 9. Evolution database ---
        try:
            project_label = f"{code}-{active}"
            evodb.init()
            evodb.insert_task(project_label, task_class, agent, resolved["leader"],
                             raw_input=task, enriched_input=enriched_task,
                             footer_ok=True, duration_s=duration, success=True)
        except Exception:
            pass

        # --- 10. Execution trace ---
        write_trace(f"{code}-{active}", task_class, agent, resolved["leader"], success, summary, duration)

        # --- 10. Obsidian note -- always sync from AI output ---
        if obsidian.is_configured():
            obsidian.write_session_note(code, active, task, agent, resolved["leader"], success, summary)
            # Sync memory & user profile after each task
            mem_text = memory_content(code, active)
            if mem_text:
                obsidian.sync_memory(code, active, mem_text, "memory")
            from .state.memory import user_content as _uc
            user_text = _uc(code, active)
            if user_text:
                obsidian.sync_memory(code, active, user_text, "user")

        # --- 11. Learning loop ---
        suggestions = analyze_completion(code, active, task, task_class, agent, success, duration, summary,
                                         footer_ok=True, raw_input=task, enriched_input=enriched_task)
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

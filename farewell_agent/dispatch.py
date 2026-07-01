"""Enhanced dispatch -- session continuity + context enrichment + learning loop."""

import json, shutil, subprocess, socket, sys, time
from pathlib import Path
from . import config
from .state.registry import get_active, get_code, get_path
from .state.memory import save_session, load_session, save_memory, memory_content
from .state.session import start_session, end_session, suggest_resume
from .intent import classify
from .context import lookup, is_ready
from .learn import analyze_completion, insights
from .workmode import current as current_mode
from .sync import render as render_config
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


LOCK_FILE = "dispatch.lock"

def _check_recovery():
    lock = config.FAREWELL_DIR / LOCK_FILE
    if lock.exists():
        stale = lock.read_text(encoding="utf-8").strip()
        info(f"Recovery: previous dispatch interrupted ({stale[:60]})")
        from .state.session import end_session, recent_sessions
        from .state.registry import get_active, get_code
        active = get_active()
        code = get_code(active)
        sessions = recent_sessions(code, active, 1)
        if sessions and sessions[0].get("status") == "started":
            end_session(code, active, sessions[0]["id"], "interrupted", None, "Process interrupted - no footer")
            info("Marked interrupted session as 'interrupted'")
        lock.unlink(missing_ok=True)
    lock.parent.mkdir(parents=True, exist_ok=True)
    return lock


def run(task: str, model_override: str | None = None):
    t0 = time.time()
    lock = _check_recovery()

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
    wf, task_class = None, None
    if not model_override:
        wf, task_class = classify(task)
        if wf:
            info(f"Workflow: {wf}")
            from .workflow import run_workflow
            run_workflow(wf, task)
            return
        if task_class:
            info(f"Intent: {task_class}")

    # --- 2. Model + agent resolution ---
    work_mode = current_mode()
    from .roles import is_org, resolve_model, resolve_agent as _resolve_agent
    agent = _resolve_agent(task_class, work_mode)

    # Determine model key: override > task_model_preferences > SPECIAL
    model_key = model_override
    if not model_key:
        try:
            roles_data = json.loads(config.ROLES_FILE.read_text(encoding="utf-8"))
            model_key = roles_data.get("task_model_preferences", {}).get(task_class or "", {}).get("model", "SPECIAL")
        except Exception:
            model_key = "SPECIAL"
    resolved = resolve_model(model_key)
    if work_mode != "plan":
        in_org = is_org(model_key)
        if not in_org:
            info(f"Model {model_key} not in org — using build agent")
            agent = "build"
        agent = _resolve_agent(task_class, work_mode, model_key)

    # Worker pool: jika WORKER, pilih specific model via select_worker()
    if model_key == "WORKER":
        from .worker import select_worker
        resolved["resolved"] = select_worker(task_class, task)

    # --- 3. Plan mode guard ---
    if work_mode == "plan" and agent not in ["planner", "architect", "docs-lookup"]:
        fail(f"Task '{task_class or 'default'}' needs build mode -- you're in PLAN.")
        write_trace(f"{code}-{active}", task_class, agent, resolved["resolved"], False, "Blocked by plan mode", time.time() - t0)
        return

    # --- 4. Config sync ---
    render_config()
    ok(f"Config synced ({agent} @ {resolved['resolved']})")

    # --- 5. Session management ---
    try:
        resume_note = suggest_resume(code, active)
        if resume_note:
            info(resume_note)
    except Exception as e:
        info(f"suggest_resume error: {e}")

    session_id = start_session(code, active, task, agent, resolved["resolved"], task_class)
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

    model_for_task = resolved["resolved"]
    model_str = f"9router/{model_for_task}"

    lock.write_text(f"{task[:100]} | {agent} @ {model_str}", encoding="utf-8")

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
            evodb.insert_task(f"{code}-{active}", task_class, agent, resolved["resolved"],
                             footer_ok=False, duration_s=duration, success=False)
            fail(f"OpenCode failed: {err_text[:300]}")
            end_session(code, active, session_id, "failed", None, f"Failed: {err_text[:100]}")
            write_trace(f"{code}-{active}", task_class, agent, resolved["resolved"], False, f"Failed: {err_text[:100]}", duration)
            lock.unlink(missing_ok=True)
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
            evodb.insert_task(project_label, task_class, agent, resolved["resolved"],
                             raw_input=task, enriched_input=enriched_task,
                             footer_ok=True, duration_s=duration, success=True)
        except Exception:
            pass

        # --- 10. Execution trace ---
        write_trace(f"{code}-{active}", task_class, agent, resolved["resolved"], success, summary, duration)

        # --- 10. Obsidian note -- always sync from AI output ---
        if obsidian.is_configured():
            obsidian.write_session_note(code, active, task, agent, resolved["resolved"], success, summary)
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
        lock.unlink(missing_ok=True)

    except subprocess.TimeoutExpired:
        duration = time.time() - t0
        end_session(code, active, session_id, "timeout", None, "Timed out (600s)")
        write_trace(f"{code}-{active}", task_class, agent, resolved["resolved"], False, "Timed out", duration)
        lock.unlink(missing_ok=True)
        fail("OpenCode timed out after 600s")
    except Exception as e:
        duration = time.time() - t0
        end_session(code, active, session_id, "error", None, f"Error: {str(e)[:100]}")
        write_trace(f"{code}-{active}", task_class, agent, resolved["resolved"], False, f"Error: {str(e)[:100]}", duration)
        lock.unlink(missing_ok=True)
        fail(f"Dispatch error: {e}")




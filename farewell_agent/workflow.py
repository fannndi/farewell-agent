"""Workflow orchestrator — multi-step task sequences for simple keywords.

Maps user-friendly keywords ("audit", "tambah fitur", "cek") to multi-step
processes that may involve multiple agents, mode switches, and reports.
"""

import shutil, subprocess, sys, time, json
from . import config
from .state.registry import get_active, get_code, get_path
from .helpers import step, ok, info, fail, c
from .sync import render as render_config


def run_workflow(wf: str, task: str):
    """Dispatch a high-level workflow."""
    dispatchers = {
        "audit": _wf_audit,
        "feature": _wf_feature,
        "fix": _wf_fix,
        "learn": _wf_learn,
        "health": _wf_health,
        "refactor": _wf_refactor,
    }
    fn = dispatchers.get(wf)
    if not fn:
        fail(f"Unknown workflow: {wf}")
        return
    fn(task)


# ── Individual workflow implementations ──


def _wf_audit(task: str):
    """Full project audit: plan mode → code review → report."""
    step("AUDIT", "Starting comprehensive project audit")

    # Step 1: ensure plan mode
    _ensure_plan_mode()

    # Step 2: Run code review agent
    _run_agent("code-reviewer", task or "audit this project comprehensively: check code quality, security, architecture, and best practices. Provide a structured report.")

    # Step 3: Security check
    _run_agent("security-reviewer", task or "audit security: check for vulnerabilities, exposed secrets, injection risks, auth issues.")

    info("Audit complete. Review the reports above.")


def _wf_feature(task: str):
    """Feature development: plan → build → review."""
    step("FEATURE", f"Starting feature development: {task[:60]}")

    # Step 1: Plan
    _run_agent("planner", f"Plan the implementation for: {task}. Output a clear step-by-step plan with files to modify.")

    # Step 2: Ensure build mode
    from .workmode import current as wm
    if wm() != "build":
        info("Switch to build mode to implement? [Y/n] ", end="")
        try:
            resp = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            resp = "y"
        if resp in ("", "y", "yes"):
            from .workmode import switch as wm_switch
            wm_switch("build")

    # Step 3: Implement
    _run_agent("build", f"Implement the feature: {task}")

    # Step 4: Review
    _run_agent("code-reviewer", f"Review the implementation of: {task}")

    info("Feature workflow complete.")


def _wf_fix(task: str):
    """Bug fix: identify → fix → verify."""
    step("FIX", f"Fixing: {task[:60]}")

    # Step 1: Diagnose
    _run_agent("build-error-resolver" if "build" in task.lower() or "compile" in task.lower() else "build",
               f"Diagnose and fix this issue: {task}")

    step("FIX", "Verification")

    info("Fix applied. Run tests to verify.")


def _wf_learn(task: str):
    """Research mode: plan mode → research → save to memory."""
    step("LEARN", f"Researching: {task[:60]}")

    _ensure_plan_mode()

    from .state.registry import get_active, get_code
    from .state.session import start_session, end_session
    active = get_active()
    code = get_code(active)
    sid = start_session(code, active, task, "docs-lookup", "research", "learn")

    _run_agent("docs-lookup" if "api" in task.lower() or "dokumentasi" in task.lower() else "planner",
               f"Research and explain: {task}. Save findings to project context.")

    end_session(code, active, sid, "completed", None, f"Researched: {task[:80]}")

    from .cli import write_context_footer
    write_context_footer()


def _wf_health(task: str):
    """System health check — same as daily."""
    step("HEALTH", "Running system health check")
    from .daily import run as daily_run
    daily_run()


def _wf_refactor(task: str):
    """Code cleanup: review dead code → clean up → verify."""
    step("REFACTOR", f"Refactoring: {task[:60]}")

    from .workmode import current as wm
    if wm() != "build":
        _ensure_plan_mode()
        info("Refactor needs build mode. Switch? [Y/n] ", end="")
        try:
            resp = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            resp = "y"
        if resp in ("", "y", "yes"):
            from .workmode import switch as wm_switch
            wm_switch("build")

    _run_agent("refactor-cleaner", task or "Clean up dead code, unused imports, redundant files. Review and refactor.")

    info("Refactor complete. Verify nothing is broken.")


# ── Helpers ──


def _ensure_plan_mode():
    """Switch to plan mode if not already."""
    from .workmode import current as wm_current, switch as wm_switch
    if wm_current() != "plan":
        wm_switch("plan")


def _run_agent(agent: str, task: str):
    """Run opencode with a specific agent and task, wait for result."""
    opencode_path = shutil.which("opencode")
    if not opencode_path:
        fail("`opencode` not found in PATH.")
        return

    active = get_active()
    code = get_code(active)
    project_path = get_path(active)

    render_config()

    cmd = [
        opencode_path, "run", task,
        "--agent", agent,
        "--format", "json",
    ]
    if project_path:
        cmd += ["--dir", project_path]

    info(f"Agent: {agent}")
    print(f"\n  {c('='*40, 'gray')}\n")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            # Print output (skip raw JSON)
            try:
                resp = json.loads(result.stdout)
                text = resp.get("text") or resp.get("content", "")
                if text:
                    print(text[:2000])
            except (json.JSONDecodeError, AttributeError):
                print(result.stdout[:2000])
            ok(f"{agent} completed")
        else:
            fail(f"{agent} failed: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        fail(f"{agent} timed out (600s)")
    except Exception as e:
        fail(f"{agent} error: {e}")

    print(f"\n  {c('='*40, 'gray')}\n")

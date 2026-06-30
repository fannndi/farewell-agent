"""Self-evolution — run one level, then commit+push."""

import subprocess, time as _time
from datetime import datetime, timezone
from pathlib import Path
from . import config
from .helpers import c, step, ok, info, fail
from .state.io import read_json, write_json
from .state.memory import save_memory, memory_content
from . import evodb

REPOS = [
    ("ECC", config.ECC_DIR, "main"),
    ("awesome-opencode", config.AWESOME_DIR, "main"),
    ("9Router", config.ROUTER_DIR, "master"),
    ("hermes-agent", config.HERMES_DIR, "main"),
    ("hermes-self-evolution", config.HERMES_SE_DIR, "main"),
]

EVOSTATE_FILE = "evostate.json"
MODEL_FOR_EVOLUTION = "SPECIAL"
LEVEL_PROMPTS = {
    1: "Buat program Python sederhana yang menerima input CLI dan mencetak output.",
    2: "Buat program dengan minimal 2 fungsi + error handling untuk input tidak valid.",
    3: "Buat program multi-file dengan modular imports dan logging.",
    4: "Buat program yang menggunakan minimal satu library eksternal (pip install).",
    5: "Buat program dengan pattern arsitektur (MVC/Repository/Service Layer).",
    6: "Buat program dengan integrasi database SQLite + CRUD operations.",
}
MAX_LEVEL = 6


def _evostate_path():
    return config.FAREWELL_DIR / EVOSTATE_FILE


def _load_state():
    return read_json(_evostate_path()) or {"level": 1, "count": 0}


def _save_state(state):
    write_json(_evostate_path(), state)


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")


def _git_add_and_push(level_msg: str):
    """Stage all, commit, push."""
    try:
        root = str(config.ROOT_DIR)
        subprocess.run(["git", "add", "-A"], cwd=root, capture_output=True, timeout=30)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root, capture_output=True, timeout=10)
        if r.returncode == 0:
            info("No changes to commit.")
            return
        msg = f"evo: {level_msg}"
        subprocess.run(["git", "commit", "-m", msg], cwd=root, capture_output=True, timeout=30)
        subprocess.run(["git", "push"], cwd=root, capture_output=True, timeout=60)
        ok(f"Committed + pushed: {msg}")
    except Exception as e:
        fail(f"Git error: {e}")


def run() -> list[str]:
    state = _load_state()

    if state["level"] > MAX_LEVEL:
        return ["Max evolution level reached."]

    changes = []

    # Step 1: pull repos + extract
    print(f"\n  {c('Evolution', 'cyan')} — Level {state['level']}/{MAX_LEVEL}\n")
    _pull_and_extract()
    changes.append("repos synced")

    # Step 2: single level
    state["count"] += 1
    weak = _find_weakest_area()
    scenario = _generate_scenario(state["level"], weak, state["count"])

    step(f"Evo {state['count']}", f"Level {state['level']} — {scenario['id']}")
    info(f"Target: {weak['target']} ({weak['reason']})")
    info(f"Task: {scenario['task'][:80]}")

    result = _execute_scenario(scenario)

    if result["passed"]:
        state["level"] += 1
        msg = f"PASS ({result['duration']:.0f}s) -> Level {state['level']}"
        ok(msg)
        changes.append(msg)
    else:
        info("FAIL — retry 1x...")
        result2 = _execute_scenario(scenario, feedback=result.get("error", ""))
        if result2["passed"]:
            state["level"] += 1
            msg = f"PASS (retry, {result2['duration']:.0f}s) -> Level {state['level']}"
            ok(msg)
            changes.append(msg)
        else:
            level_down = max(1, state["level"] - 1)
            state["level"] = level_down
            msg = f"FAIL (2x) -> Level {level_down}"
            fail(msg)
            changes.append(msg)

    _save_state(state)
    _record(changes)
    _git_add_and_push(changes[-1])

    print(f"\n  {c('Done', 'green')} — Level {state['level']}/{MAX_LEVEL}")
    return changes


def _pull_and_extract():
    for label, repo_dir, branch in REPOS:
        if not (repo_dir / ".git").exists():
            continue
        r = _git_pull(repo_dir, branch)
        if r.get("updated"):
            ok(f"{label}: {r['summary']}")
        elif r.get("reason") == "up to date":
            pass
    try:
        script = config.ROOT_DIR / "scripts" / "extract_knowledge.py"
        if script.exists():
            subprocess.run([sys.executable, str(script)], cwd=str(config.ROOT_DIR),
                          capture_output=True, timeout=300)
    except Exception:
        pass


def _git_pull(repo_dir, branch):
    try:
        before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_dir),
                                capture_output=True, text=True, timeout=10).stdout.strip()[:8]
        r = subprocess.run(["git", "pull", "--ff-only", "origin", branch], cwd=str(repo_dir),
                          capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return {"updated": False, "reason": r.stderr.strip()[:200]}
        after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_dir),
                               capture_output=True, text=True, timeout=10).stdout.strip()[:8]
        if before == after:
            return {"updated": False, "reason": "up to date"}
        log = subprocess.run(["git", "log", f"{before}..{after}", "--oneline"], cwd=str(repo_dir),
                            capture_output=True, text=True, timeout=10)
        commits = [l.strip() for l in log.stdout.strip().splitlines() if l.strip()] if log.returncode == 0 else []
        return {"updated": True, "summary": f"{before} -> {after} ({len(commits)} commit(s))"}
    except Exception as e:
        return {"updated": False, "reason": str(e)}


def _find_weakest_area() -> dict:
    candidates = []
    perf = evodb.model_performance()

    # 1. Footer violation
    for p in perf:
        rate = p["footers"] / p["total"] if p["total"] else 1
        if rate < 0.95:
            candidates.append({"target": p["model"], "reason": f"footer {rate:.0%}",
                             "priority": 1, "type": "footer"})

    # 2. Low success rate per class
    try:
        from .learn import _patterns_path
        from .state.registry import get_active, get_code
        patterns = read_json(_patterns_path(get_code(get_active()), get_active()))
        for cls, stats in patterns.get("by_class", {}).items():
            rate = stats["success"] / stats["total"]
            if rate < 0.7:
                candidates.append({"target": cls, "reason": f"success {rate:.0%}",
                                 "priority": 2, "type": "class"})
        # 3. Untested class
        for cls in ["feature", "fix", "audit", "learn", "refactor", "deploy"]:
            if cls not in patterns.get("by_class", {}):
                candidates.append({"target": cls, "reason": "untested",
                                 "priority": 3, "type": "gap"})
    except Exception:
        pass

    if not candidates:
        candidates.append({"target": "default", "reason": "all healthy, random",
                         "priority": 99, "type": "random"})

    candidates.sort(key=lambda x: x["priority"])
    return candidates[0]


def _generate_scenario(level: int, weak: dict, count: int) -> dict:
    base = LEVEL_PROMPTS.get(level, LEVEL_PROMPTS[MAX_LEVEL])
    if weak["type"] == "footer":
        base += " PASTIKAN output diakhiri dengan FOOTER."
    elif weak["target"] in ("fix", "deploy"):
        base += f" Fokus pada skenario {weak['target']}."
    elif weak["target"] == "audit":
        base += " Sertakan analisis keamanan dan best practices."
    elif weak["target"] == "refactor":
        base += " Tulis ulang dengan pattern yang lebih baik."
    return {
        "id": f"L{level}-{weak['target']}-{count}",
        "level": level,
        "task": base,
        "target": weak["target"],
        "reason": weak["reason"],
    }


def _execute_scenario(scenario: dict, feedback: str = "") -> dict:
    t0 = _time.time()
    task = scenario["task"]
    if feedback:
        task += f"\n\nPrevious attempt feedback: {feedback[:200]}"
        task += "\nPerbaiki error dan pastikan program berjalan dengan benar."

    try:
        from .dispatch import run as dispatch_run
        dispatch_run(task, model_override=MODEL_FOR_EVOLUTION)
        passed = True
    except SystemExit:
        passed = False
    except Exception as e:
        passed = False

    duration = _time.time() - t0
    return {"passed": passed, "duration": duration, "error": "" if passed else str(e) if 'e' in dir() else "unknown"}


def _record(changes: list[str]):
    try:
        from .state.registry import get_active, get_code
        active = get_active()
        code = get_code(active)
        mem = memory_content(code, active) or "# MEMORY - project facts\n"
        entry = f"\n## Evolution ({_now()})\n" + "\n".join(f"- {c}" for c in changes[-5:])
        if len(mem) + len(entry) <= 2100:
            save_memory(code, active, mem + entry)
        from . import obsidian
        if obsidian.is_configured():
            obsidian.write_session_note(code, active, "evolution", "auto", MODEL_FOR_EVOLUTION, True,
                                         "; ".join(changes[:3]))
    except Exception:
        pass

"""Evolution — pull 5 tools repo, extract knowledge, auto-apply improvements."""

import json, subprocess
from datetime import datetime, timezone
from . import config
from .helpers import c, step, ok, info, fail
from .state.io import read_json, write_json
from .state.memory import save_memory, memory_content

REPOS = [
    ("ECC", config.ECC_DIR, "main"),
    ("awesome-opencode", config.AWESOME_DIR, "main"),
    ("9Router", config.ROUTER_DIR, "master"),
    ("hermes-agent", config.HERMES_DIR, "main"),
    ("hermes-self-evolution", config.HERMES_SE_DIR, "main"),
]


def run() -> list[str]:
    changes = []
    print(f"\n  {c('Evolution', 'cyan')}\n  {c('='*40, 'cyan')}\n")

    step("1/3", "Git pull 5 tool repos")
    for label, repo_dir, branch in REPOS:
        if not (repo_dir / ".git").exists():
            info(f"{label}: not cloned, skipping")
            continue
        result = _git_pull(repo_dir, branch)
        if result.get("updated"):
            ok(f"{label}: {result['summary']}")
            for c_ in result.get("new_commits", [])[:3]:
                info(f"  {c_}")
        elif result.get("reason") == "up to date":
            info(f"{label}: up to date")
        else:
            info(f"{label}: {result.get('reason', 'error')}")

    step("2/3", "Extract knowledge to Obsidian vault")
    _run_extract_knowledge()
    ok("Knowledge vault updated")
    changes.append("Knowledge vault extracted")

    step("3/3", "Auto-detect improvements")
    ecc_new = _detect_new_ecc_skills()
    if ecc_new:
        _update_manifests(ecc_new)
        ok(f"ECC: {len(ecc_new)} new skills auto-registered")
        changes.append(f"ECC: {len(ecc_new)} new skills")

    ver = _check_9router_version()
    if ver:
        info(f"9Router: {ver}")
        changes.append(f"9Router: {ver}")

    from .sync import render
    render()
    ok("Config auto-regenerated")
    changes.append("Config regenerated")

    _record_evolution(changes)
    if changes:
        print(f"\n  {c('Evolution complete', 'green')}")
        for ch in changes:
            info(ch)
    else:
        info("No changes detected")

    return changes


def _git_pull(repo_dir, branch):
    if not (repo_dir / ".git").exists():
        return {"updated": False, "reason": "not a git repo"}
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
        return {"updated": True, "before": before, "after": after,
                "new_commits": commits, "summary": f"{before} -> {after} ({len(commits)} commit(s))"}
    except Exception as e:
        return {"updated": False, "reason": str(e)}


def _run_extract_knowledge():
    script = config.ROOT_DIR / "scripts" / "extract_knowledge.py"
    if not script.exists():
        info("extract_knowledge.py not found")
        return
    try:
        import sys
        subprocess.run([sys.executable, str(script)], cwd=str(config.ROOT_DIR), timeout=300)
    except Exception as e:
        info(f"Extract skipped: {e}")


def _detect_new_ecc_skills() -> list[str]:
    new_skills = []
    try:
        index_file = config.ECC_DIR / "skills" / "index.json"
        if not index_file.exists():
            return new_skills
        data = json.loads(index_file.read_text(encoding="utf-8"))
        skills = data.get("skills", []) if isinstance(data, dict) else data
        known = set()
        for mf in config.MANIFESTS_DIR.glob("*.json"):
            try:
                m = json.loads(mf.read_text(encoding="utf-8"))
                for s in m.get("skills", []):
                    known.add(s)
            except Exception: pass
        for s in skills:
            name = s.get("name") or s if isinstance(s, str) else ""
            if name and name not in known:
                new_skills.append(name)
    except Exception: pass
    return new_skills


def _update_manifests(new_skills: list[str]):
    for mf in config.MANIFESTS_DIR.glob("*.json"):
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
            existing = set(data.get("skills", []))
            added = [s for s in new_skills if s not in existing]
            if added:
                data["skills"] = data.get("skills", []) + added
                write_json(mf, data)
        except Exception: pass
    from .indexer import write_active_skills
    write_active_skills()


def _check_9router_version() -> str:
    try:
        pkg = config.ROUTER_DIR / "package.json"
        if pkg.exists():
            v = json.loads(pkg.read_text(encoding="utf-8")).get("version", "")
            return f"v{v}" if v else ""
    except Exception: pass
    return ""


def _record_evolution(changes: list[str]):
    try:
        from .state.registry import get_active, get_code
        active = get_active()
        code = get_code(active)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        mem = memory_content(code, active) or "# MEMORY - project facts\n"
        entry = f"\n## Evolution ({now})\n" + "\n".join(f"- {c}" for c in changes)
        if len(mem) + len(entry) <= 2100:
            save_memory(code, active, mem + entry)
        from . import obsidian
        if obsidian.is_configured():
            obsidian.write_session_note(code, active, "evolution", "system", "auto", True,
                                         "; ".join(changes[:3]))
    except Exception: pass

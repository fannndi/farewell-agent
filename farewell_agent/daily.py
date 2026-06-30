import json, shutil, socket, subprocess, time, urllib.request
from pathlib import Path
from . import config
from .helpers import c, step, ok, skip, fail, info
from .sync import render as render_config

def run():
    print(f"\n  {c('Daily', 'cyan')}\n  {c('='*40, 'cyan')}\n")

    step("1/4", "Start 9Router")
    started = _ensure_9router()
    if not started: fail("9Router failed to start")

    step("2/4", "Upstream ECC + awesome-opencode + 9Router")
    for label, repo_dir, branch in [
        ("ECC", config.ECC_DIR, "main"),
        ("awesome-opencode", config.AWESOME_DIR, "main"),
        ("9Router", config.ROUTER_DIR, "master"),
    ]:
        result = _git_pull(repo_dir, branch)
        if result.get("updated"):
            ok(f"{label}: {result['summary']}")
            for c_ in result.get("new_commits", [])[:3]:
                info(f"  {c_}")
        elif result.get("reason") == "up to date":
            info(f"{label}: up to date")
        else:
            info(f"{label}: {result.get('reason', 'error')}")

    step("3/4", "Sync opencode.jsonc")
    render_config()
    ok("Config regenerated")
    _index_awesome()

    step("4/4", "Readiness check")
    health = _check_9router()
    ecc = _check_ecc()
    github = _check_github_release()
    combos = _load_combos()
    _print_report(health, ecc, github, combos)

    # Save checkpoint
    from .state.registry import get_active, get_code
    active = get_active()
    code = get_code(active)
    from .state.memory import save_session
    save_session(code, active, "Daily checkpoint completed")

def _ensure_9router() -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(("127.0.0.1", 20128))
    sock.close()
    if result == 0: return True

    skip("9Router not running — starting...")
    router_dir = config.ROUTER_DIR
    standalone = router_dir / ".next" / "standalone"
    src = router_dir / ".next" / "static"
    dst = standalone / "public" / "_next" / "static"
    if src.exists() and dst.parent.parent.exists():
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            (shutil.copytree if item.is_dir() else shutil.copy2)(item, dst / item.name, dirs_exist_ok=True)
    try:
        env_file = router_dir / ".env"
        data_dir = str(config._9router_db().parent.parent)
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("DATA_DIR="): data_dir = line.split("=", 1)[1].strip(); break
        env = {"PORT": "20128", "NODE_ENV": "production", "DATA_DIR": data_dir, "INITIAL_PASSWORD": "123456"}
        node_cmd = ["node", str(standalone / "server.js")] if standalone.exists() else ["npx", "next", "start", "-p", "20128"]
        proc = subprocess.Popen(node_cmd, cwd=str(router_dir), env={**os.environ, **env},
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            time.sleep(1)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1)
            try:
                if s.connect_ex(("127.0.0.1", 20128)) == 0:
                    ok(f"9Router started (PID: {proc.pid})")
                    pid_file = config.STATE_DIR / "9router.pid"
                    pid_file.parent.mkdir(parents=True, exist_ok=True); pid_file.write_text(str(proc.pid))
                    s.close(); return True
            finally: s.close()
        skip("9Router start timed out (30s)")
    except Exception as e: skip(f"9Router start failed: {e}")
    return False

def _git_pull(repo_dir: Path, branch: str = "main") -> dict:
    if not (repo_dir / ".git").exists():
        return {"updated": False, "reason": "not a git repo"}
    try:
        before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_dir),
                                capture_output=True, text=True, timeout=10).stdout.strip()[:8]
        r = subprocess.run(["git", "pull", "--ff-only", "origin", branch], cwd=str(repo_dir),
                          capture_output=True, text=True, timeout=60)
        if r.returncode != 0: return {"updated": False, "reason": r.stderr.strip()[:200]}
        after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_dir),
                               capture_output=True, text=True, timeout=10).stdout.strip()[:8]
        if before == after: return {"updated": False, "reason": "up to date"}
        log = subprocess.run(["git", "log", f"{before}..{after}", "--oneline"], cwd=str(repo_dir),
                            capture_output=True, text=True, timeout=10)
        commits = [l.strip() for l in log.stdout.strip().splitlines() if l.strip()] if log.returncode == 0 else []
        return {"updated": True, "before": before, "after": after,
                "new_commits": commits, "summary": f"{before} -> {after} ({len(commits)} commit(s))"}
    except Exception as e: return {"updated": False, "reason": str(e)}

def _index_awesome():
    try:
        from .awesome_indexer import load_all_entries
        plugs, themes, ags, projs, res = load_all_entries()
        info(f"awesome: {len(plugs)}p, {len(themes)}t, {len(ags)}a, {len(projs)}pr")
    except Exception:
        info("awesome: not available (not cloned?)")

def _check_9router() -> dict:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); sock.settimeout(2)
    r = sock.connect_ex(("127.0.0.1", 20128)); sock.close()
    if r != 0: return {"running": False}
    try:
        data = json.loads(urllib.request.urlopen("http://localhost:20128/api/version", timeout=3).read())
        return {"running": True, "version": data.get("currentVersion")}
    except: return {"running": True, "version": None}

def _check_ecc() -> dict:
    try:
        subprocess.run(["git", "fetch", "origin", "main"], cwd=str(config.ECC_DIR), capture_output=True, text=True, timeout=15)
        behind = subprocess.run(["git", "rev-list", "--count", "HEAD..origin/main"], cwd=str(config.ECC_DIR),
                               capture_output=True, text=True, timeout=10)
        commits = int(behind.stdout.strip()) if behind.returncode == 0 and behind.stdout.strip() else 0
        return {"commits_behind": commits}
    except Exception as e: return {"commits_behind": 0, "reason": str(e)}

def _check_github_release() -> dict:
    try:
        req = urllib.request.Request("https://api.github.com/repos/decolua/9router/releases/latest",
                                     headers={"User-Agent": "farewell-agent"})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        return {"tag": data.get("tag_name", ""), "published": data.get("published_at", "")}
    except: return {"error": "GitHub unreachable"}

def _load_combos() -> list[dict]:
    try:
        import sqlite3
        db = config._9router_db()
        if not db.exists(): return []
        conn = sqlite3.connect(str(db))
        cur = conn.execute("SELECT name, kind, models FROM combos")
        combos = []
        for row in cur:
            try: models = json.loads(row[2]) if row[2] else []
            except: models = []
            combos.append({"key": row[0], "kind": row[1] or "-", "models": models})
        conn.close()
        return combos
    except: return []

def _print_report(health, ecc, github, combos):
    print(f"\n  {c('='*40, 'cyan')}\n  {c('Readiness', 'cyan')}\n  {c('='*40, 'cyan')}")
    if health["running"]: ok(f"9Router v{health.get('version') or '?'}")
    else: fail("9Router NOT running")
    if ecc.get("commits_behind", 0) > 0: info(f"ECC: {ecc['commits_behind']} behind")
    else: ok("ECC: up to date")
    if "error" in github: fail(f"GitHub: {github['error']}")
    else:
        local_ver = None
        pkg = config.ROUTER_DIR / "package.json"
        if pkg.exists():
            try: local_ver = json.loads(pkg.read_text()).get("version")
            except: pass
        tag = github.get("tag", "").lstrip("v")
        if local_ver and tag != local_ver:
            info(f"GitHub: v{tag} — update available!")
        else: ok(f"GitHub: {github.get('tag', '?')}")
    total_models = sum(len(c.get("models", [])) for c in combos)
    for c_ in combos:
        ms = ", ".join(c_["models"][:3])
        if len(c_["models"]) > 3: ms += f" +{len(c_['models'])-3}"
        info(f"  {c_['key']:<20} ({c_['kind']:<8}) <- {ms}")
    ok(f"{len(combos)} combos, {total_models} models")
    print(f"  {c('='*40, 'cyan')}\n")

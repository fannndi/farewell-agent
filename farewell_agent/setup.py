"""Setup — clone dependency repos (routers, skills, registries, references)."""

import subprocess, sys, time
from pathlib import Path
from . import config
from .helpers import step, ok, skip, fail, info

REPOS = [
    ("9Router", config.ROUTER_DIR, "https://github.com/decolua/9router.git", "master"),
    ("ECC", config.ECC_DIR, "https://github.com/affaan-m/ECC.git", "main"),
    ("awesome-opencode", config.AWESOME_DIR, "https://github.com/awesome-opencode/awesome-opencode.git", "main"),
    ("Hermes Agent", config.HERMES_DIR, "https://github.com/NousResearch/hermes-agent.git", "main"),
    ("Hermes Self-Evolution", config.HERMES_SE_DIR, "https://github.com/NousResearch/hermes-agent-self-evolution.git", "main"),
]

def run():
    """Clone all dependency repos if not already present."""
    print(f"\n  {'='*40}\n  {'Setup: Clone dependencies':^38}\n  {'='*40}\n")
    all_ok = True
    for name, path, url, branch in REPOS:
        step(name, f"Cloning {url}")
        if path.exists() and (path / ".git").exists():
            skip(f"{name} already exists at {path}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            r = subprocess.run(
                ["git", "clone", "--branch", branch, "--depth", "1", url, str(path)],
                capture_output=True, text=True, timeout=300
            )
            if r.returncode == 0:
                ok(f"{name} cloned ({branch})")
            else:
                fail(f"{name} failed: {r.stderr.strip()[:200]}")
                all_ok = False
        except subprocess.TimeoutExpired:
            fail(f"{name} timed out (5 min)")
            all_ok = False
        except FileNotFoundError:
            fail("git not found in PATH. Install Git first: https://git-scm.com")
            sys.exit(1)

    print(f"\n  {'='*40}")
    if all_ok:
        ok("All dependencies ready")
    else:
        info("Some dependencies failed — check errors above")
    print(f"  {'='*40}\n")

    # Link 9Router build artifacts from farewell-assistant if available
    _link_9router_build()

    # Generate config after clone
    try:
        from .sync import render
        render()
        ok("Config regenerated")
    except Exception as e:
        info(f"Config generation skipped: {e}")

def _link_9router_build():
    """Link .next/ and node_modules/ from existing farewell-assistant checkout."""
    fa_root = config.ROOT_DIR.parent / "farewell-assistant"
    if not fa_root.exists():
        info("No fare well-assistant found — 9Router source only (build needed)")
        return
    for sub in [".next", "node_modules"]:
        src = fa_root / "9router" / sub
        dst = config.ROUTER_DIR / sub
        if src.exists() and not dst.exists():
            try:
                import os
                os.symlink(str(src), str(dst), target_is_directory=True)
                ok(f"Linked 9router/{sub}/ from farewell-assistant")
            except (OSError, NotImplementedError):
                info(f"Could not link {sub} — 9Router source only")

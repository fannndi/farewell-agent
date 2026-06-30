import os
from datetime import date
from pathlib import Path
from . import config
from .indexer import find_matching

SIGNATURES = [
    ("pyproject.toml", "python"), ("setup.py", "python"), ("requirements.txt", "python"),
    ("Cargo.toml", "rust"), ("go.mod", "golang"),
    ("pubspec.yaml", "flutter"), ("package.json", "nodejs"),
    ("Dockerfile", "docker"),
]

FRAMEWORK_HINTS = {
    "next.config": "nextjs", "nuxt.config": "vue", "vite.config": "react",
    "angular.json": "angular", "vue.config": "vue", "svelte.config": "svelte",
    "django": "django", "fastapi": "fastapi", "flask": "flask",
    "pom.xml": "java", "build.gradle": "kotlin",
}

DOM_MAP = {"flutter": "DART", "nextjs": "TYPESCRIPT", "react": "TYPESCRIPT",
           "vue": "JAVASCRIPT", "python": "PYTHON", "golang": "GOLANG",
           "rust": "RUST", "kotlin": "KOTLIN", "nodejs": "NODE"}

def analyze(path_str: str) -> dict:
    path = Path(path_str).resolve()
    if not path.is_dir():
        raise ValueError(f"Path not found: {path}")

    stack = _probe_stack(path)
    ptype = _detect_type(stack)
    dominan = DOM_MAP.get(ptype, "UNKNOWN")
    name = path.name

    from .state.registry import register
    result = register(name, str(path), stack, ptype, dominan)

    _write_manifest(result["code"], name, stack)
    _inject_symlinks(path, result["code"], name)
    _extract_guide_book(result["code"], name, stack)
    _switch_to_project(result["name"])

    return {
        "action": result["action"], "code": result["code"], "name": name,
        "type": ptype, "dominan": dominan, "stack": stack,
        "skills": find_matching(stack), "path": str(path),
    }

def _probe_stack(path: Path) -> list[str]:
    hints = set()
    entries = list(path.iterdir()) if path.is_dir() else []

    for fname, stack_name in SIGNATURES:
        if (path / fname).exists():
            hints.add(stack_name)
        else:
            for e in entries:
                if e.is_dir() and (e / fname).exists():
                    hints.add(stack_name)
                    break

    for e in entries:
        if e.is_dir():
            for hint, stack_name in FRAMEWORK_HINTS.items():
                if any(f.name.startswith(hint) for f in e.iterdir()):
                    hints.add(stack_name)
        elif e.is_file():
            for hint, stack_name in FRAMEWORK_HINTS.items():
                if e.name.startswith(hint):
                    hints.add(stack_name)

    return sorted(hints) if hints else ["nodejs"]

def _detect_type(stack: list[str]) -> str:
    priority = ["flutter", "nextjs", "react", "vue", "angular", "nodejs", "python", "golang", "rust", "kotlin"]
    for p in priority:
        if p in stack: return p
    return stack[0] if stack else "unknown"

def _write_manifest(code: str, name: str, stack: list[str]):
    manifest = {
        "schema_version": 1,
        "project": f"{code}-{name}",
        "stack": stack,
        "skills": find_matching(stack),
        "generated_at": date.today().isoformat(),
    }
    mf = config.MANIFESTS_DIR / f"{code}-{name}.json"
    import json
    mf.parent.mkdir(parents=True, exist_ok=True)
    tmp = mf.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    tmp.replace(mf)

def _inject_symlinks(project_path: Path, code: str, name: str):
    """Create .farewell/ in target project with symlinks to central resources."""
    target = project_path / ".farewell"
    target.mkdir(parents=True, exist_ok=True)

    # Symlink skills directory
    skills_link = target / "skills"
    if not skills_link.exists() and config.ECC_DIR.exists():
        src = config.ECC_DIR / "skills"
        _symlink(src, skills_link)

    # Symlink AGENTS.md
    agents_link = target / "AGENTS.md"
    agents_src = config.ECC_DIR / "AGENTS.md"
    if not agents_link.exists() and agents_src.exists():
        _symlink(agents_src, agents_link)

    # Symlink instructions
    instr_link = target / "instructions"
    instr_src = config.ROOT_DIR / "instructions"
    if not instr_link.exists() and instr_src.exists():
        _symlink(instr_src, instr_link)

    # Create per-project memory dir
    mem_dir = target / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)

    # Create per-project context dir
    ctx_dir = target / "context"
    ctx_dir.mkdir(parents=True, exist_ok=True)

def _extract_guide_book(code: str, name: str, stack: list[str]):
    """Copy relevant vault articles to projects/{code}-{name}/ as panduan."""
    try:
        from .obsidian import _vault_path
        vault = _vault_path()
        if not vault: return
        proj_dir = vault / f"{code}-{name}"
        proj_dir.mkdir(parents=True, exist_ok=True)
        for s in stack:
            src_dir = vault.parent / "stacks" / s
            if not src_dir.exists(): continue
            articles = sorted(src_dir.glob("*.md"))
            if not articles: continue
            lines = [f"# Panduan {s.upper()}\n"]
            for a in articles[:10]:
                text = a.read_text(encoding="utf-8", errors="ignore")[:500]
                lines.append(f"\n## {a.stem}\n{text}\n---\n")
            (proj_dir / f"guide-{s}.md").write_text("".join(lines), encoding="utf-8")
    except Exception:
        pass


def _switch_to_project(name: str):
    """Auto-switch active project after setup."""
    try:
        from .state.registry import load, save
        reg = load()
        reg["active"] = name
        save(reg)
        from .cli import write_context_footer
        write_context_footer()
    except Exception:
        pass


def _symlink(src: Path, dst: Path):
    """Cross-platform symlink (fallback to copy on Windows if needed)."""
    try:
        dst.symlink_to(src, target_is_directory=src.is_dir())
    except (OSError, NotImplementedError):
        if src.is_dir():
            import shutil
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

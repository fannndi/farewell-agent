"""Knowledge context -- always consult Obsidian vault (buku panduan) before action."""

import re
from pathlib import Path
from . import config
from .intent import classify_workflow, classify_task

_VAULT_CACHE = None
_STACK_MAP = {
    "web": {"react", "nextjs", "vue", "frontend", "typescript", "javascript", "css", "html",
            "angular", "tailwind", "ui", "ux", "responsive", "svelte"},
    "android": {"kotlin", "android", "compose", "jetpack", "kmp", "gradle", "material"},
    "flutter": {"flutter", "dart", "cupertino", "widget"},
    "backend": {"python", "django", "fastapi", "flask", "nodejs", "express", "golang",
                "go", "rust", "actix", "spring", "java", "kotlin", "graphql", "rest",
                "api", "grpc", "sqlalchemy"},
    "devops": {"docker", "kubernetes", "deployment", "ci", "cd", "github-actions",
               "terraform", "ansible", "nginx", "proxy"},
    "security": {"security", "auth", "oauth", "jwt", "cors", "csrf", "xss", "sql-injection",
                 "encryption", "authentication", "authorization", "vulnerability"},
    "database": {"database", "postgres", "postgresql", "mysql", "sqlite", "migrations",
                 "sql", "nosql", "mongodb", "redis", "query", "schema"},
    "common": {"git", "testing", "tdd", "code-review", "error-handling", "refactor",
               "logging", "ci", "lint", "format", "clean-code", "solid"},
}

def _vault_dir() -> Path | None:
    global _VAULT_CACHE
    if _VAULT_CACHE is not None:
        return _VAULT_CACHE
    _VAULT_CACHE = config.obsidian_vault("_farewell-agent")
    return _VAULT_CACHE

def is_ready() -> bool:
    return _vault_dir() is not None

def _detect_stacks(text: str) -> list[str]:
    """Map task text to stack folders."""
    lower = text.lower()
    matched = []
    for stack, keywords in _STACK_MAP.items():
        if any(kw in lower for kw in keywords):
            matched.append(stack)
    return matched

def _walk_md(dir: Path) -> list[Path]:
    if not dir or not dir.exists():
        return []
    return [f for f in dir.iterdir() if f.suffix == ".md" and f.is_file()]

def _search_files(files: list[Path], keywords: list[str], vault: Path) -> list[dict]:
    results = []
    for f in files:
        name = f.stem.lower()
        score = sum(1 for kw in keywords if kw in name)
        if score == 0:
            text_preview = f.read_text(encoding="utf-8", errors="ignore")[:200].lower()
            score = sum(1 for kw in keywords if kw in text_preview)
        if score > 0:
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")[:500]
                title = text.split("\n")[0].lstrip("#").strip() if text else name
                snippet = ""
                for line in text.split("\n")[1:]:
                    s = line.strip()
                    if s and not s.startswith("---") and not s.startswith("#"):
                        snippet = s[:200]
                        break
                results.append({
                    "file": f.name,
                    "title": title,
                    "snippet": snippet,
                    "score": score,
                    "path": str(f.relative_to(vault)),
                })
            except Exception:
                pass
    return results

def search(query: str, max_results: int = 5) -> list[dict]:
    vault = _vault_dir()
    if not vault:
        return []

    keywords = _extract_keywords(query.lower())
    results = []

    # 1. universal/ecc/
    results += _search_files(_walk_md(vault / "universal" / "ecc"), keywords, vault)

    # 2. universal/ root
    results += _search_files([f for f in _walk_md(vault / "universal") if f.name != ".gitkeep"], keywords, vault)

    # 3. stacks/{matched}/
    stacks = _detect_stacks(query)
    for s in stacks:
        results += _search_files(_walk_md(vault / "stacks" / s), keywords, vault)

    # 4. active project
    try:
        from .state.registry import get_active, get_code
        active = get_active()
        code = get_code(active)
        results += _search_files(_walk_md(vault / "projects" / f"{code}-{active}"), keywords, vault)
    except Exception:
        pass

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]

def _get_project_scope() -> str | None:
    """Return project code prefix for vault scope."""
    try:
        from .state.registry import get_active, get_code
        return f"{get_code(get_active())}-{get_active()}"
    except Exception:
        return None

def lookup(task: str) -> str:
    vault = _vault_dir()
    if not vault:
        return ""

    wf = classify_workflow(task)
    task_lower = task.lower()
    keywords = _extract_keywords(task_lower)
    blocks = []
    matched_stacks = _detect_stacks(task)
    project_scope = _get_project_scope()

    # 1. Workflow guides
    wf_to_vault = {
        "audit": ["universal/ecc/ECC-Security.md", "universal/ecc/ECC-Skills-Index.md"],
        "feature": ["universal/ecc/ECC-Skills-Index.md"],
        "fix": ["universal/ecc/ECC-Skills-Index.md"],
        "learn": ["universal/ecc/ECC-Skills-Index.md"],
        "health": ["projects/001-farewell-agent/9router.md"],
        "refactor": ["universal/ecc/ECC-Skills-Index.md"],
    }
    if wf and wf in wf_to_vault:
        for rel_path in wf_to_vault[wf]:
            fp = vault / rel_path
            if fp.exists():
                text = fp.read_text(encoding="utf-8", errors="ignore")[:800]
                title = text.split("\n")[0].lstrip("#").strip() if text else rel_path
                blocks.append(f"[Guide] **{title}**\n{text[:500]}")

    # 2. Stack-specific skills
    found_skills = []
    for stack in matched_stacks:
        stack_dir = vault / "stacks" / stack
        if stack_dir.exists():
            for f in _walk_md(stack_dir):
                name = f.stem.lower()
                kw_matches = sum(1 for kw in keywords if kw in name)
                if kw_matches >= 1 or stack in task_lower:
                    try:
                        text = f.read_text(encoding="utf-8", errors="ignore")[:200]
                        title = text.split("\n")[0].lstrip("#").strip() if text else name
                        first_line = ""
                        for line in text.split("\n")[1:]:
                            if line.strip() and not line.startswith("---") and not line.startswith("#"):
                                first_line = line.strip()[:120]
                                break
                        found_skills.append(f"  - [[{f.stem}]]: {first_line}")
                    except Exception:
                        pass

    # 3. Universal ECC skills (2+ keyword match)
    ecc_dir = vault / "universal" / "ecc"
    if ecc_dir.exists():
        for f in _walk_md(ecc_dir):
            name = f.stem.lower()
            kw_matches = sum(1 for kw in keywords if kw in name)
            if kw_matches >= 2:
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")[:200]
                    title = text.split("\n")[0].lstrip("#").strip() if text else name
                    first_line = ""
                    for line in text.split("\n")[1:]:
                        if line.strip() and not line.startswith("---") and not line.startswith("#"):
                            first_line = line.strip()[:120]
                            break
                    found_skills.append(f"  - [[{f.stem}]]: {first_line}")
                except Exception:
                    pass

    if found_skills:
        blocks.append(f"[Skills] **Skill terkait** ({len(found_skills)})\n" + "\n".join(found_skills[:5]))

    # 4. Project-specific knowledge
    if project_scope:
        project_dir = vault / "projects" / project_scope
        if project_dir.exists():
            proj_files = [f for f in _walk_md(project_dir) if f.name not in ("MEMORY.md", "USER.md", "Session-Log.md", ".gitkeep")]
            if proj_files:
                snippets = []
                for f in proj_files:
                    try:
                        text = f.read_text(encoding="utf-8", errors="ignore")[:300]
                        title = text.split("\n")[0].lstrip("#").strip() if text else f.stem
                        snippets.append(f"  - [[{f.stem}]]: {title}")
                    except Exception:
                        pass
                if snippets:
                    blocks.append(f"[Project] **{project_scope}**\n" + "\n".join(snippets))

    # 5. Specific topic files (with updated paths)
    special_topics = {
        "docker": "universal/ecc/docker-patterns.md",
        "rust": "universal/ecc/rust-patterns.md",
        "flutter": "universal/ecc/dart-flutter-patterns.md",
        "python": "universal/ecc/python-patterns.md",
        "react": "universal/ecc/react-patterns.md",
        "golang": "universal/ecc/golang-patterns.md",
        "kotlin": "universal/ecc/kotlin-patterns.md",
        "security": "universal/ecc/ECC-Security.md",
        "deploy": "universal/ecc/deployment-patterns.md",
        "android": "universal/ecc/android-clean-architecture.md",
        "database": "universal/ecc/database-migrations.md",
        "nextjs": "universal/ecc/frontend-patterns.md",
    }
    for topic, rel_path in special_topics.items():
        if topic in task_lower:
            fp = vault / rel_path
            if fp.exists():
                text = fp.read_text(encoding="utf-8", errors="ignore")[:500]
                lines = text.split("\n")
                title = lines[0].lstrip("#").strip() if lines else topic
                snippet = "\n".join(l[1] for l in enumerate(lines[1:6]) if l[1].strip() and not l[1].startswith("---"))
                blocks.append(f"[Topic] **{title}**\n{snippet[:300]}")

    if not blocks:
        return ""

    result = "\n\n---\n### Buku Panduan\n" + "\n\n".join(blocks) + "\n---\n"
    return result

def _extract_keywords(text: str) -> list[str]:
    stop_words = {"the", "a", "an", "in", "to", "for", "of", "on", "at", "by", "with",
                  "from", "and", "or", "but", "is", "are", "was", "were", "be", "been",
                  "this", "that", "these", "those", "fix", "add", "change", "update",
                  "remove", "delete", "create", "make", "do", "get", "set", "need", "want",
                  "please", "help", "can", "will", "would", "could", "should", "error",
                  "bug", "issue", "problem", "feature", "task", "work", "done", "project",
                  "ini", "itu", "di", "ke", "dan", "atau", "yang", "untuk", "dengan",
                  "saya", "kamu", "aku", "dia", "kami", "mereka", "bisa", "tidak", "sudah",
                  "belum", "akan", "sedang", "lagi", "baru", "ada", "pada", "dari", "oleh",
                  "tambah", "buat", "bikin", "cek", "cari", "lihat", "kasih", "pake"}
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b', text)
    return [w.lower() for w in words if w.lower() not in stop_words][:15]

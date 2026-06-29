"""Knowledge context — always consult Obsidian vault (buku panduan) before action."""

import re, textwrap
from pathlib import Path
from . import config
from .intent import classify_workflow, classify_task

_VAULT_CACHE = None


def _vault_dir() -> Path | None:
    """Read OBSIDIAN_VAULT from api-key.txt, cached."""
    global _VAULT_CACHE
    if _VAULT_CACHE is not None:
        return _VAULT_CACHE
    key_file = config.ROOT_DIR / "api-key.txt"
    if not key_file.exists():
        _VAULT_CACHE = None
        return None
    for line in key_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("OBSIDIAN_VAULT="):
            p = Path(line.split("=", 1)[1].strip()) / "_farewell-agent"
            if p.exists():
                _VAULT_CACHE = p
                return p
    _VAULT_CACHE = None
    return None


def is_ready() -> bool:
    """Check if Obsidian vault (guide book) is available."""
    return _vault_dir() is not None


def search(query: str, max_results: int = 5) -> list[dict]:
    """Search the vault for knowledge relevant to query. Returns list of {file, title, snippet, score}."""
    vault = _vault_dir()
    if not vault:
        return []

    keywords = _extract_keywords(query.lower())
    results = []

    # Search ECC skill files
    ecc_dir = vault / "ecc"
    if ecc_dir.exists():
        for f in ecc_dir.iterdir():
            if not f.suffix == ".md" or not f.is_file():
                continue
            name = f.stem.lower()
            score = sum(1 for kw in keywords if kw in name)
            if score > 0:
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")[:500]
                    title = text.split("\n")[0].lstrip("#").strip() if text else name
                    # Find first non-empty line as snippet
                    snippet = ""
                    for line in text.split("\n")[1:]:
                        stripped = line.strip()
                        if stripped and not stripped.startswith("---") and not stripped.startswith("#"):
                            snippet = stripped[:200]
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

    # Search root files
    for f in vault.iterdir():
        if not f.suffix == ".md" or not f.is_file():
            continue
        if f.name in ("_Index.md", ".gitkeep"):
            continue
        name = f.stem.lower()
        score = sum(1 for kw in keywords if kw in name or kw in f.read_text(encoding="utf-8", errors="ignore")[:200].lower())
        if score > 0:
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")[:300]
                title = text.split("\n")[0].lstrip("#").strip() if text else name
                snippet = text.split("\n")[1][:200] if len(text.split("\n")) > 1 else ""
                results.append({
                    "file": f.name,
                    "title": title,
                    "snippet": snippet.strip(),
                    "score": score,
                    "path": str(f.relative_to(vault)),
                })
            except Exception:
                pass

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]


def lookup(task: str) -> str:
    """Look up relevant knowledge in the vault. Returns formatted markdown block (or empty)."""
    vault = _vault_dir()
    if not vault:
        return ""

    wf = classify_workflow(task)
    tc = classify_task(task)
    task_lower = task.lower()
    keywords = _extract_keywords(task_lower)

    blocks = []

    # 1. If workflow detected, load related category file
    wf_to_vault = {
        "audit": ["ecc/ECC-Security.md", "ecc/ECC-Skills-Index.md"],
        "feature": ["ecc/ECC-Skills-Index.md"],
        "fix": ["ecc/ECC-Skills-Index.md"],
        "learn": ["ecc/ECC-Skills-Index.md"],
        "health": ["9router.md"],
        "refactor": ["ecc/ECC-Skills-Index.md"],
    }
    if wf and wf in wf_to_vault:
        for rel_path in wf_to_vault[wf]:
            fp = vault / rel_path
            if fp.exists():
                text = fp.read_text(encoding="utf-8", errors="ignore")[:800]
                title = text.split("\n")[0].lstrip("#").strip() if text else rel_path
                blocks.append(f"[Guide] **{title}**\n{text[:500]}")

    # 2. Search skill files — require 2+ keyword matches, or match domain
    ecc_dir = vault / "ecc"
    found_skills = []
    domain_skills = {
        "python": ["python-patterns", "python-testing", "fastapi-patterns", "django-patterns"],
        "flutter": ["dart-flutter-patterns", "flutter-dart-code-review", "compose-multiplatform-patterns"],
        "rust": ["rust-patterns", "rust-testing"],
        "docker": ["docker-patterns", "deployment-patterns"],
        "security": ["ECC-Security"],
        "golang": ["golang-patterns", "golang-testing"],
        "react": ["react-patterns", "frontend-patterns"],
        "database": ["database-migrations", "postgres-patterns"],
        "deploy": ["deployment-patterns"],
        "test": ["e2e-testing"],
        "git": ["git-workflow"],
    }
    matched_domains = [d for d in domain_skills if d in task_lower]
    if ecc_dir.exists():
        for f in ecc_dir.iterdir():
            if not f.suffix == ".md" or not f.is_file():
                continue
            name = f.stem.lower()
            # Require 2+ keyword matches for generic skills, or domain match
            kw_matches = sum(1 for kw in keywords if kw in name)
            domain_match = any(skill_name in name for d in matched_domains for skill_name in domain_skills[d])
            if kw_matches >= 2 or domain_match:
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

    # 3. Check specific topic files
    special_topics = {
        "docker": "ecc/docker-patterns.md",
        "rust": "ecc/rust-patterns.md",
        "flutter": "ecc/dart-flutter-patterns.md",
        "python": "ecc/python-patterns.md",
        "react": "ecc/react-patterns.md",
        "nextjs": "ecc/nextjs-turbopack.md",
        "golang": "ecc/golang-patterns.md",
        "kotlin": "ecc/kotlin-patterns.md",
        "security": "ecc/ECC-Security.md",
        "deploy": "ecc/deployment-patterns.md",
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
    """Extract meaningful keywords from text."""
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

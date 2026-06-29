"""Knowledge-aware context enricher — scan Obsidian vault for relevant skill snippets."""

import re
from pathlib import Path
from . import config
from .intent import classify

def enrich(task: str, project_code: str, project_name: str) -> str:
    """Search Obsidian vault for knowledge relevant to this task. Returns markdown snippet."""
    vault = _vault_path()
    if not vault:
        return ""

    task_lower = task.lower()
    kw = _extract_keywords(task_lower)
    task_class = classify(task)

    blocks = []

    # 1. If task has a specific intent class, load that category
    if task_class:
        cat_file = vault / "ecc" / f"ECC-{task_class.split('-')[0].title()}.md"
        if not cat_file.exists():
            cat_file = vault / "ecc" / "ECC-Skills-Index.md"
        if cat_file.exists():
            text = cat_file.read_text(encoding="utf-8", errors="ignore")[:1500]
            blocks.append(f"### Relevant Skill Category: {task_class}\n{text}")

    # 2. Search individual skill files for keyword matches
    ecc_dir = vault / "ecc"
    if ecc_dir.exists():
        matches = []
        for f in ecc_dir.iterdir():
            if not f.suffix == ".md" or not f.is_file():
                continue
            name = f.stem.lower()
            score = sum(1 for kw_ in kw if kw_ in name)
            if score > 0:
                try:
                    first_line = f.read_text(encoding="utf-8", errors="ignore")[:200].split("\n")[0]
                    matches.append((score, name, first_line))
                except Exception:
                    pass
        matches.sort(reverse=True)
        if matches:
            top = matches[:3]
            lines = [f"- [[{m[1]}]] — {m[2][:80]}" for m in top]
            blocks.append("### Relevant Skills\n" + "\n".join(lines))

    # 3. Check special files
    specials = {
        "security": "ecc/ECC-Security.md",
        "deploy": None,
        "rust": "ecc/rust-patterns.md" if (vault / "ecc" / "rust-patterns.md").exists() else None,
        "kotlin": "ecc/kotlin-patterns.md" if (vault / "ecc" / "kotlin-patterns.md").exists() else None,
    }
    for key, fpath in specials.items():
        if key in task_lower and fpath:
            fp = vault / fpath
            if fp.exists():
                text = fp.read_text(encoding="utf-8", errors="ignore")[:1000]
                blocks.append(f"### Related: {key.title()}\n{text}")

    if not blocks:
        return ""

    result = "\n\n---\n### Knowledge Context\n" + "\n\n".join(blocks) + "\n---\n"
    return result[:3000]  # cap at 3K chars


def _vault_path() -> Path | None:
    """Read OBSIDIAN_VAULT from api-key.txt."""
    key_file = config.ROOT_DIR / "api-key.txt"
    if not key_file.exists():
        return None
    for line in key_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("OBSIDIAN_VAULT="):
            p = Path(line.split("=", 1)[1].strip())
            vault_dir = p / "_farewell-agent"
            if vault_dir.exists():
                return vault_dir
    return None


def _extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from task text."""
    stop_words = {"the", "a", "an", "in", "to", "for", "of", "on", "at", "by", "with",
                  "from", "and", "or", "but", "is", "are", "was", "were", "be", "been",
                  "this", "that", "these", "those", "fix", "add", "change", "update",
                  "remove", "delete", "create", "make", "do", "get", "set", "need",
                  "want", "please", "help", "can", "will", "would", "could", "should",
                  "error", "bug", "issue", "problem", "feature", "task", "work", "done"}
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9-]{2,}\b', text)
    return [w.lower() for w in words if w.lower() not in stop_words][:15]

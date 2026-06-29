"""Extract knowledge from ECC, awesome-opencode, 9Router -> Obsidian vault."""

import sys, os, re, yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from farewell_agent import config
from farewell_agent.obsidian import vault_path

vault = Path(vault_path())
if not vault.exists():
    print(f"Vault not found: {vault_path()}. Set OBSIDIAN_VAULT in api-key.txt")
    sys.exit(1)

agent_dir = vault / "_farewell-agent"
agent_dir.mkdir(exist_ok=True)
(agent_dir / ".gitkeep").write_text("")
ecc_dir = agent_dir / "ecc"
ecc_dir.mkdir(exist_ok=True)

# ── CATEGORY MAPPING ──
CAT_MAP = {
    "python": "ECC-Python", "flutter": "ECC-Flutter", "dart": "ECC-Flutter",
    "react": "ECC-Frontend", "nextjs": "ECC-Frontend", "frontend": "ECC-Frontend",
    "vue": "ECC-Frontend", "nodejs": "ECC-Backend", "backend": "ECC-Backend",
    "golang": "ECC-Backend", "rust": "ECC-Backend", "kotlin": "ECC-Backend",
    "swift": "ECC-Backend", "database": "ECC-DevOps", "docker": "ECC-DevOps",
    "devops": "ECC-DevOps", "infra": "ECC-DevOps", "workflow": "ECC-Workflow",
    "testing": "ECC-Workflow", "security": "ECC-Security", "git": "ECC-Workflow",
    "tdd": "ECC-Workflow", "accessibility": "ECC-Workflow",
}


def extract_ecc():
    """Extract all 271 ECC skills -> categorized markdown files."""
    skills_dir = config.ECC_DIR / "skills"
    if not skills_dir.exists():
        print("ECC not found. Run: py -m farewell_agent setup")
        return

    all_skills = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8", errors="ignore")
        fm = {}
        m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if m:
            try:
                fm = yaml.safe_load(m.group(1)) or {}
            except Exception:
                pass
        name = fm.get("name", skill_dir.name)
        desc = fm.get("description", "")
        tags = fm.get("metadata", {}).get("hermes", {}).get("tags", [])
        cat = fm.get("metadata", {}).get("hermes", {}).get("category", tags[0] if tags else "uncategorized")
        all_skills.append({
            "name": name, "slug": skill_dir.name,
            "desc": desc, "category": cat, "tags": tags,
        })

    print(f"ECC: {len(all_skills)} skills")

    # Master index
    with open(ecc_dir / "ECC-Skills-Index.md", "w", encoding="utf-8") as f:
        f.write("# ECC Skills Index\n\n")
        f.write(f"Total: **{len(all_skills)} skills** -- dari [affaan-m/ECC](https://github.com/affaan-m/ECC)\n\n")
        f.write("| # | Skill | Description | Tags |\n")
        f.write("|---|-------|-------------|------|\n")
        for i, s in enumerate(all_skills, 1):
            desc = s["desc"][:80] if s["desc"] else "-"
            tags = " ".join(f"`{t}`" for t in s["tags"][:3])
            f.write(f"| {i} | **{s['name']}** | {desc} | {tags} |\n")

    # Group by category
    grouped = {}
    for s in all_skills:
        key = "ECC-Other"
        for tag in s["tags"]:
            mapped = CAT_MAP.get(tag.lower())
            if mapped:
                key = mapped
                break
        if key == "ECC-Other":
            for pattern, mapped in CAT_MAP.items():
                if pattern in s["category"].lower():
                    key = mapped
                    break
        grouped.setdefault(key, []).append(s)

    for gname, skills in sorted(grouped.items()):
        path = ecc_dir / f"{gname}.md"
        label = gname.replace("-", " / ").replace("ECC", "ECC")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {label}\n\n{len(skills)} skills\n\n")
            for s in skills:
                f.write(f"## [[{s['slug']}]] -- {s['name']}\n\n")
                if s["desc"]:
                    f.write(f"{s['desc']}\n\n")
                if s["tags"]:
                    f.write(f"Tags: " + " ".join(f"`{t}`" for t in s["tags"]) + "\n\n")
                f.write("---\n\n")

    # Individual skill files (top 120)
    count = 0
    for s in all_skills:
        if count >= 120:
            break
        src = skills_dir / s["slug"] / "SKILL.md"
        if not src.exists():
            continue
        text = src.read_text(encoding="utf-8", errors="ignore")
        clean = re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, flags=re.DOTALL).strip()
        with open(ecc_dir / f"{s['slug']}.md", "w", encoding="utf-8") as f:
            f.write(f"# {s['name']}\n\n")
            f.write(f"Source: `ecc/skills/{s['slug']}/SKILL.md`\n\n---\n\n")
            f.write(clean[:3000])
        count += 1

    print(f"  -> {count} individual skill files written")


def extract_awesome():
    """Extract awesome-opencode catalog."""
    data_dir = config.AWESOME_DIR / "data"
    if not data_dir.exists():
        print("awesome-opencode not found")
        return

    categories = {
        "plugins": [], "themes": [], "agents": [], "projects": [], "resources": [],
    }
    for cat in categories:
        d = data_dir / cat
        if not d.exists():
            continue
        for f in d.glob("*.yaml"):
            try:
                with open(f, encoding="utf-8") as fh:
                    data = yaml.safe_load(fh) or {}
                categories[cat].append(data)
            except Exception:
                pass

    total = sum(len(v) for v in categories.values())
    print(f"awesome-opencode: {total} entries")

    with open(agent_dir / "awesome-opencode.md", "w", encoding="utf-8") as f:
        f.write("# Awesome Opencode Catalog\n\n")
        f.write("Dari [awesome-opencode/awesome-opencode](https://github.com/awesome-opencode/awesome-opencode)\n\n")
        for cat, entries in categories.items():
            f.write(f"## {cat.title()} ({len(entries)})\n\n")
            for e in entries:
                name = e.get("name", "?")
                desc = e.get("tagline") or e.get("description", "")
                repo = e.get("repo", "")
                f.write(f"- **{name}** -- {desc}\n")
                if repo:
                    f.write(f"  [{repo}]({repo})\n")
            f.write("\n")

    print("  -> awesome-opencode.md written")


def extract_9router():
    """Extract 9Router README and key docs."""
    router_dir = config.ROUTER_DIR
    if not router_dir.exists():
        print("9Router not found")
        return

    readme = router_dir / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8", errors="ignore")[:5000]
        with open(agent_dir / "9router.md", "w", encoding="utf-8") as f:
            f.write("# 9Router -- LLM Router & Proxy\n\n")
            f.write(f"Repo: https://github.com/decolua/9router\n\n---\n\n")
            f.write(text)

    # List combo names from SQLite
    combo_db = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
    if combo_db.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(str(combo_db))
            rows = conn.execute("SELECT name, kind, models FROM combos").fetchall()
            conn.close()
            with open(agent_dir / "9router.md", "a", encoding="utf-8") as f:
                f.write(f"\n\n## Active Combos ({len(rows)})\n\n")
                f.write("| Combo | Kind | Models |\n")
                f.write("|-------|------|--------|\n")
                for row in rows:
                    models = ", ".join(json.loads(row[2]) if row[2] else [])
                    f.write(f"| {row[0]} | {row[1] or '-'} | {models} |\n")
        except Exception:
            pass

    print("  -> 9router.md written")


def extract_hermes():
    """Extract Hermes Agent docs."""
    hermes_dir = config.HERMES_DIR
    if hermes_dir.exists():
        readme = hermes_dir / "README.md"
        if readme.exists():
            text = readme.read_text(encoding="utf-8", errors="ignore")[:4000]
            with open(agent_dir / "hermes-agent.md", "w", encoding="utf-8") as f:
                f.write("# Hermes Agent -- Self-Improving AI Agent\n\n")
                f.write("Repo: https://github.com/NousResearch/hermes-agent (205k stars)\n\n---\n\n")
                f.write(text)

    se_dir = config.HERMES_SE_DIR
    if se_dir.exists():
        readme = se_dir / "README.md"
        plan = se_dir / "PLAN.md"
        if readme.exists():
            text = readme.read_text(encoding="utf-8", errors="ignore")[:3000]
            with open(agent_dir / "hermes-self-evolution.md", "w", encoding="utf-8") as f:
                f.write("# Hermes Agent Self-Evolution\n\n")
                f.write("Repo: https://github.com/NousResearch/hermes-agent-self-evolution (4.4k stars)\n\n---\n\n")
                f.write(text)
        if plan.exists():
            plan_text = plan.read_text(encoding="utf-8", errors="ignore")[:5000]
            with open(agent_dir / "hermes-self-evolution.md", "a", encoding="utf-8") as f:
                f.write("\n\n## PLAN.md (architecture)\n\n")
                f.write(plan_text)

    print("  -> hermes-agent.md + hermes-self-evolution.md written")


def write_master_index():
    """Write master index linking all knowledge bases."""
    lines = [
        "# Farewell Agent -- Knowledge Base",
        "",
        "Selamat datang di knowledge base AI kamu! Ini hasil ekstraksi dari semua repo terkait:",
        "",
        "## ECC Skills (271 skills)",
        "",
        "| File | Isi |",
        "|------|-----|",
        "| [[ecc/ECC-Skills-Index]] | Daftar lengkap 271 skills |",
        "| [[ecc/ECC-Python]] | Python, Django, FastAPI |",
        "| [[ecc/ECC-Flutter]] | Flutter, Dart |",
        "| [[ecc/ECC-Frontend]] | React, NextJS, Vue |",
        "| [[ecc/ECC-Backend]] | NodeJS, Go, Rust, Kotlin, Swift |",
        "| [[ecc/ECC-DevOps]] | Docker, K8s, Database |",
        "| [[ecc/ECC-Workflow]] | Git, TDD, Coding Standards |",
        "| [[ecc/ECC-Security]] | Security review, Verification |",
        "| [[ecc/ECC-Other]] | Uncategorized skills |",
        "",
        "## awesome-opencode",
        "",
        "| File | Isi |",
        "|------|-----|",
        "| [[awesome-opencode]] | 129 plugins, 9 agents, 61 projects |",
        "",
        "## 9Router",
        "",
        "| File | Isi |",
        "|------|-----|",
        "| [[9router]] | LLM Router docs + active combos |",
        "",
        "## Hermes Agent (205k stars)",
        "",
        "| File | Isi |",
        "|------|-----|",
        "| [[hermes-agent]] | Self-improving AI agent overview |",
        "| [[hermes-self-evolution]] | Evolutionary skill optimization (DSPy+GEPA) |",
        "",
        "---",
        "*Generated by farewell-agent extract-knowledge*",
        "",
    ]
    with open(agent_dir / "_Index.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  -> _Index.md written")


if __name__ == "__main__":
    import json
    print("\nExtracting knowledge to Obsidian vault...\n")
    extract_ecc()
    extract_awesome()
    extract_9router()
    extract_hermes()
    write_master_index()
    print(f"\nDone! Files in: {agent_dir}\n")

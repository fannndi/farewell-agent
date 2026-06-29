from pathlib import Path
from . import config

def _load_yaml(path: Path) -> dict:
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def load_all() -> tuple[list, list, list, list, list]:
    plugins, themes, agents, projects, resources = [], [], [], [], []
    base = config.AWESOME_DIR / "data"
    for category, container in [("plugins", plugins), ("themes", themes),
                                 ("agents", agents), ("projects", projects),
                                 ("resources", resources)]:
        d = base / category
        if d.exists():
            for f in d.glob("*.yaml"):
                container.append(_load_yaml(f))
    return plugins, themes, agents, projects, resources

def recommend(stack: list[str]) -> list:
    _, _, _, projects, _ = load_all()
    lower_stack = [s.lower() for s in stack]
    scored = []
    for p in projects:
        score = 0
        for t in p.get("tags", []):
            if t.lower() in lower_stack: score += 3
            if p.get("name", "").lower() in t.lower() or t.lower() in p.get("name", "").lower(): score += 2
        if score > 0:
            p["_score"] = score
            scored.append(p)
    return sorted(scored, key=lambda x: x["_score"], reverse=True)[:20]

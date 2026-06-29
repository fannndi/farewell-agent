import json, os
from pathlib import Path
from . import config
from .state.io import read_json, write_json
from .state.registry import get_active, get_code
from .indexer import write_active_skills
import subprocess

def render():
    template_path = config.ROOT_DIR / "opencode.template.jsonc"
    output_path = config.ROOT_DIR / "opencode.jsonc"
    if not template_path.exists():
        return False

    template = template_path.read_text(encoding="utf-8")
    team_state = _get_team()
    models = _load_config()
    combos = _load_combo_names()

    team_map = {"ON": "divisi", "TIM": "tim", "BAWAHAN": "bawahan"}
    tier_label = team_map.get(team_state, "tim")

    from .roles import resolve_for_tier
    resolved = resolve_for_tier(tier_label)

    leader = resolved["leader"]
    special = resolved["special"]
    worker = resolved["worker"]

    provider_models = set(combos)
    skip_keys = {"NINEROUTER_API_KEY", "OBSIDIAN_VAULT"}
    for k, v in models.items():
        if k in skip_keys: continue
        if v and k not in combos:
            for m in v.split(","):
                m = m.strip()
                if m: provider_models.add(m)
    model_entries = []
    for i, m in enumerate(sorted(provider_models)):
        comma = "," if i < len(provider_models) - 1 else ""
        model_entries.append(f'        "{m}": {{ "name": "{m}" }}{comma}')
    models_json = "{\n" + "\n".join(model_entries) + "\n      }"

    skill_paths = _load_skill_paths()
    skill_paths_json = json.dumps(skill_paths)

    content = template
    content = content.replace("${MODELS_JSON}", models_json)
    content = content.replace("${LEADER}", leader)
    content = content.replace("${SPECIAL}", special)
    content = content.replace("${WORKER}", worker)
    if "${HELPER}" in content:
        content = content.replace("${HELPER}", worker)
    content = content.replace("${SKILL_PATHS}", skill_paths_json)

    tmp = output_path.with_suffix(".jsonc.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(output_path)
    return True

def _get_team() -> str:
    try:
        f = config.FAREWELL_DIR / "team.json"
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8")).get("team", "TIM")
    except Exception: pass
    return "TIM"

def _load_config() -> dict:
    models = {}
    f = config.ROOT_DIR / "api-key.txt"
    if not f.exists(): return models
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" not in line or line.startswith("#"): continue
        k, v = line.split("=", 1)
        models[k.strip()] = v.strip()
    return models

def _load_combo_names() -> set[str]:
    try:
        import sqlite3
        db = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
        if not db.exists(): return set()
        conn = sqlite3.connect(str(db))
        names = {row[0] for row in conn.execute("SELECT name FROM combos")}
        conn.close()
        return names
    except Exception:
        return set()

def _load_skill_paths() -> list[str]:
    mf = config.STATE_DIR / "active-skills.json"
    if mf.exists():
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
            return data.get("paths", ["ecc/skills", ".farewell/custom-skills"])
        except Exception: pass
    return ["ecc/skills", ".farewell/custom-skills"]

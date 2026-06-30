import os, platform
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ECC_DIR = ROOT_DIR / "ecc"
ROUTER_DIR = ROOT_DIR / "9router"
AWESOME_DIR = ROOT_DIR / "awesome-opencode"
STATE_DIR = ROOT_DIR / ".opencode"
FAREWELL_DIR = ROOT_DIR / ".farewell"
REGISTRY_FILE = FAREWELL_DIR / "registry.json"
WORK_MODE_FILE = STATE_DIR / "work-mode.json"
PROJECT_CONTEXT_DIR = FAREWELL_DIR / "context"
MEMORY_DIR = FAREWELL_DIR / "memory"
MANIFESTS_DIR = FAREWELL_DIR / "manifests"
CUSTOM_SKILLS_DIR = FAREWELL_DIR / "custom-skills"
COST_LOG = FAREWELL_DIR / "cost-log.csv"
COST_BUDGET = FAREWELL_DIR / "cost-budget.json"
ROLES_FILE = FAREWELL_DIR / "roles.json"
HERMES_DIR = ROOT_DIR / "hermes-agent"
HERMES_SE_DIR = ROOT_DIR / "hermes-agent-self-evolution"

def is_windows() -> bool:
    return platform.system() == "Windows"

def _env_path() -> Path:
    return ROOT_DIR / "api-key.txt"

def load_env() -> dict[str, str]:
    models = {}
    f = _env_path()
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" not in line or line.startswith("#"): continue
            k, v = line.split("=", 1)
            models[k.strip()] = v.strip()
    return models

def _9router_db() -> Path:
    if is_windows():
        base = Path(os.environ.get("APPDATA", ""))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "9router" / "db" / "data.sqlite"

def obsidian_vault(suffix: str = "_farewell-agent") -> Path | None:
    env = load_env()
    p = env.get("OBSIDIAN_VAULT", "")
    if not p: return None
    vault = Path(p) / suffix
    return vault if vault.exists() else None

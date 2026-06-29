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

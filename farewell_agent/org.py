"""Org hierarchy -- reads from org_registry + resolve in roles.json."""

from . import config
from .state.io import read_json
from .roles import resolve_model

def _org():
    roles = read_json(config.ROLES_FILE) or {}
    return roles.get("org_registry", []), roles.get("resolve", {})

def chart():
    registry, resolve = _org()
    print(f"\n  Org Registry ({len(registry)} models):")
    for m in registry:
        entry = resolve.get(m, {})
        r = resolve_model(m)
        print(f"    {m:<15} -> {r['resolved']:<30} role={entry.get('role','?')} agent={entry.get('agent','build')}")
    print()

def roles():
    registry, resolve = _org()
    print()
    for m in registry:
        entry = resolve.get(m, {})
        r = resolve_model(m)
        print(f"  [{m}] {entry.get('role','?')}")
        print(f"  Model: {r['resolved']}")
        print(f"  Agent: {entry.get('agent','build')}")
        print()

def workflow():
    print("\n  Workflow (build mode):")
    print("    1. User task -> dispatch")
    print("    2. Classify intent -> pilih model key (LEADER/SPECIAL/WORKER)")
    print("    3. Dispatch -> OpenCode agent langsung eksekusi")
    print("    4. Review + FOOTER -> user")
    print("  Workflow (plan mode):")
    print("    1. Planner/Architect - read-only, eksplorasi kode")
    print("    2. Output: plan/rekomendasi, tanpa perubahan file\n")

def priority():
    print("\n  Role Priority:")
    print("    LEADER  -> orchestrator: perintah/strategi/plan")
    print("    SPECIAL -> executor: eksekusi task utama")
    print("    WORKER  -> executor: task murah/grunt\n")

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
    print("    2. Cek org_registry -> model terdaftar?")
    print("       YES -> orchestrator (team agent) + delegation")
    print("       NO  -> fallback build agent (single)")
    print("    3. Orchestrator (read-only):")
    print("       a. Planner (WORKER) - riset, plan, review")
    print("       b. Executor (WORKER) - coding, fix (write-only)")
    print("    4. Review + FOOTER -> user")
    print("  Workflow (plan mode):")
    print("    1. Planner/Architect - read-only, eksplorasi kode")
    print("    2. Output: plan/rekomendasi, tanpa perubahan file\n")

def priority():
    print("\n  Access Priority:")
    print("    1. Orchestrator (SPECIAL) -- read-only, delegasi")
    print("    2. Planner (WORKER) -- read-only, riset & review")
    print("    3. Executor (WORKER) -- write-only, coding & fix")
    print("    4. Build (LEADER) -- fallback, full access\n")

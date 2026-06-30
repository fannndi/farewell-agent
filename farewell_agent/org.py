from . import config
from .state.io import read_json
from .roles import resolve_for_tier

def _load_org_data() -> dict:
    return read_json(config.ROLES_FILE) or {}

def _model_for_role(role_name: str, tier: str) -> str:
    r = resolve_for_tier(tier)
    mapping = {"Director AI": r["leader"], "Deputy Director AI": r["leader"],
               "Team Leader": r["special"], "Senior Backend Engineer": r["worker"],
               "Junior Reviewer": r["worker"]}
    return mapping.get(role_name, r["worker"])

def _active_labels():
    team_state = _current_team()
    tier_name = {"ON": "divisi", "TIM": "tim", "BAWAHAN": "bawahan"}.get(team_state, "tim")
    return team_state, tier_name

def chart():
    team_state, tier_name = _active_labels()
    r = resolve_for_tier(tier_name)
    print(f"\n  Team: {team_state}")
    print(f"  Leader: {r['leader']} | Special: {r['special']} | Worker: {r['worker']}\n")
    lines = [
        "  Boss (User)",
        "  |-- Director AI",
        f"  |   Model : {r['leader']} — strategi, final review",
        "  |-- Deputy Director AI",
        f"  |   Model : {r['leader']} — validasi, second opinion",
        "  +-- Team Leader (Anda)",
        f"  |   Model : {r['special']} — orkestrasi, delegasi",
        "  |   |-- Senior Backend Engineer",
        f"  |   |   Model : {r['worker']} — eksekusi teknis",
        "  |   |-- Junior Reviewer",
        f"  |       Model : {r['worker']} — validasi kode",
        "  |-- Planner",
        f"  |   Model : {r['worker']} — task breakdown",
        "  +-- Architect",
        f"      Model : {r['special']} — system design",
    ]
    print("\n" + "\n".join(lines) + "\n")

def roles():
    team_state, tier_name = _active_labels()
    r = resolve_for_tier(tier_name)
    data = [
        ("[BOSS] User", "-", "Pengguna", ["Menentukan objective", "Prioritas", "Menyetujui hasil"]),
        ("[DIRECTOR] Director AI", r["leader"], "Pegawai Tetap", ["Strategi", "Final review", "High-risk decisions"]),
        ("[DEPUTY] Deputy Director AI", r["leader"], "Pegawai Tetap", ["Validasi", "Second opinion"]),
        ("[LEADER] Team Leader", r["special"], "Pegawai Tetap", ["Orkestrasi", "Delegasi", "Review hasil"]),
        ("[SENIOR] Senior Backend Engineer", r["worker"], "Pegawai Tetap", ["Backend", "API", "DB", "Security"]),
        ("[JUNIOR] Junior Reviewer", r["worker"], "Junior", ["Bug finding", "Code review", "Edge cases"]),
        ("[PLANNER] Planner", r["worker"], "Pegawai Tetap", ["Task breakdown", "Research"]),
        ("[ARCHITECT] Architect", r["special"], "Pegawai Tetap", ["System design", "Architecture decisions"]),
    ]
    print()
    for title, model, status, auths in data:
        print(f"  {title}")
        print(f"  Model: {model}")
        print(f"  Status: {status}")
        for a in auths: print(f"    - {a}")
        print()

def workflow():
    steps = [
        "1. User → Task description",
        "2. Intent classify → workflow / task class",
        "3. Agent resolution → team / senior-engineer / director / etc",
        "4. LEADER = strategi | SPECIAL = orkestrasi | WORKER = eksekusi",
        "5. Team Leader delegates to subagents",
        "6. Subagent executes → reports back",
        "7. Team Leader reviews → presents to user",
        "8. Save session + sync to Obsidian",
        "9. Learning loop + auto-evolve every 10 tasks",
    ]
    print("\n  Workflow:")
    for s in steps: print(f"    {s}")
    print()

def priority():
    tier_name = _active_labels()[1]
    r = resolve_for_tier(tier_name)
    print(f"\n  Decision Priority ({tier_name.upper()}):")
    print(f"    1. Boss (User) — Keputusan tertinggi")
    print(f"    2. Director AI ({r['leader']}) — Strategi & final review")
    print(f"    3. Deputy Director AI ({r['leader']}) — Validasi strategi")
    print(f"    4. Team Leader ({r['special']}) — Orkestrasi harian")
    print(f"    5. Senior Engineer ({r['worker']}) — Eksekusi teknis")
    print(f"    6. Junior Reviewer ({r['worker']}) — Validasi silang")
    print("  Keputusan berdasarkan bukti teknis, bukan voting.\n")

def _current_team() -> str:
    f = config.FAREWELL_DIR / "team.json"
    if f.exists():
        try:
            import json
            return json.loads(f.read_text(encoding="utf-8")).get("team", "TIM")
        except: pass
    return "TIM"

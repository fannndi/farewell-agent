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

def chart():
    team_state = _current_team()
    tier_name = {"ON": "divisi", "TIM": "tim", "BAWAHAN": "bawahan"}.get(team_state, "tim")
    r = resolve_for_tier(tier_name)
    lines = [
        "  Boss (User)",
        "  |-- Director AI",
        f"  |   Model : {r['leader']}",
        "  |-- Deputy Director AI",
        f"  |   Model : {r['leader']}",
        "  +-- Team Leader AI (Anda)",
        f"      Model : {r['special']}",
        "      |-- Senior Backend Engineer",
        f"      |   Model : {r['worker']}",
        "      |-- Junior Reviewer I",
        f"      |   Model : {r['worker']}",
        "      |-- Junior Reviewer II",
        f"      |   Model : {r['worker']}",
        "      +-- Junior Reviewer III",
        f"          Model : {r['worker']}",
    ]
    print("\n" + "\n".join(lines) + "\n")

def roles():
    team_state = _current_team()
    tier_name = {"ON": "divisi", "TIM": "tim", "BAWAHAN": "bawahan"}.get(team_state, "tim")
    r = resolve_for_tier(tier_name)
    data = [
        ("[BOSS] User", "-", "Pengguna", ["Menentukan objective", "Prioritas", "Menyetujui hasil"]),
        ("[DIRECTOR] Director AI", r["leader"], "Pegawai Tetap", ["Strategi", "Work Order", "Final review"]),
        ("[DEPUTY] Deputy Director AI", r["leader"], "Pegawai Tetap", ["Validasi", "Second opinion"]),
        ("[LEADER] Team Leader", r["special"], "Pegawai Tetap", ["Orkestrasi", "Audit frontend", "Review"]),
        ("[SENIOR] Senior Backend Engineer", r["worker"], "Pegawai Tetap", ["Backend", "API", "DB", "Security"]),
        ("[JUNIOR] Junior Reviewer I", r["worker"], "Junior", ["Bug Finding", "Edge Cases"]),
        ("[JUNIOR] Junior Reviewer II", r["worker"], "Junior", ["Code Style", "Refactoring"]),
        ("[JUNIOR] Junior Reviewer III", r["worker"], "Junior", ["Architecture", "Scalability"]),
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
        "1. Pahami objective — Baca task description",
        "2. Analisis ruang lingkup — Scope, dependensi, risiko",
        "3. Intent classify — Task class → model override",
        "4. Resolve agent + model — roles.json + api-key.txt",
        "5. Dispatch ke OpenCode — `opencode run --agent .. --model ..`",
        "6. Eksekusi agent — tool calls, file edits, tests",
        "7. Review output — Code review otomatis",
        "8. Save session memory — Checkpoint",
        "9. Update MEMORY.md — Catat pelajaran",
    ]
    print("\n  Workflow:")
    for s in steps: print(f"    {s}")
    print()

def priority():
    roles_data = [
        "1. Boss (User) — Keputusan tertinggi",
        "2. Director AI — Strategi & final review",
        "3. Deputy Director AI — Validasi strategi",
        "4. Team Leader — Orkestrasi harian",
        "5. Senior Backend Engineer — Eksekusi teknis",
        "6. Junior Reviewer — Validasi silang",
    ]
    print("\n  Decision Priority:")
    for r_ in roles_data: print(f"    {r_}")
    print("  Keputusan berdasarkan bukti teknis, bukan voting.\n")

def _current_team() -> str:
    f = config.FAREWELL_DIR / "team.json"
    if f.exists():
        try:
            import json
            return json.loads(f.read_text(encoding="utf-8")).get("team", "TIM")
        except: pass
    return "TIM"

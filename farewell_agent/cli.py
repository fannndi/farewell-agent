"""CLI dispatcher — routes commands to modules, zero business logic."""

import argparse, json
from . import config
from .helpers import c

def cmd_workmode(args):
    from .workmode import switch
    switch(args.action)

def cmd_team(args):
    from .team import switch, status
    if args.action == "status": status()
    else: switch(args.action)

def cmd_setup(args):
    from .setup import run as setup_run
    setup_run()

def cmd_daily(args):
    from .daily import run
    run()

def cmd_status(args):
    from .state.registry import get_active, get_code
    from .workmode import current as wm_current
    from .state.memory import memory_content, user_content
    from .indexer import get_skills
    from .awesome_indexer import load_all
    from .cost import budget_status
    active = get_active()
    mode = wm_current()
    code = get_code(active)
    team = _get_team_label()
    skills = get_skills(code, active)
    sk = f" | Skills: {len(skills)}" if skills else ""
    plugs, themes, ags, projs, res = load_all()
    ao = f" | awesome: {len(plugs)}p/{len(ags)}a/{len(projs)}pr"
    budget = budget_status()
    bgt = f" | Budget: ${budget['spent_today']:.2f}/day ${budget['spent_month']:.2f}/mo"
    mem = memory_content(code, active)
    mem_flag = " | MEMORY: yes" if mem else ""
    try:
        from .obsidian import is_configured, vault_path
        ob_flag = f" | Obsidian: {vault_path()}" if is_configured() else ""
    except Exception: ob_flag = ""
    print(f"\n  {c(f'Farewell: ON | {code}-{active} | {mode.upper()}{sk}{ao}{bgt}{mem_flag}{ob_flag} | {team}', 'cyan')}\n")

def cmd_project(args):
    from .state.registry import list_all, load, save
    from .state.memory import save_session
    from .helpers import info
    if args.action == "switch" and args.code:
        reg = load()
        for name, info_ in reg.get("projects", {}).items():
            if info_.get("project_code") == args.code:
                old_active = reg.get("active", "")
                old_code = list_all()
                for p in old_code:
                    if p["name"] == old_active:
                        save_session(p["code"], old_active, f"switched to {args.code}-{name}")
                        break
                reg["active"] = name
                save(reg)
                write_context_footer()
                print(f"\n  {c(f'[ACTIVE] {args.code}-{name}', 'green')}\n")
                return
        info(f"Project code '{args.code}' not found")
    elif args.code and args.action != "switch":
        # Bare `project <code>` also works
        args.action = "switch"
        cmd_project(args)
    else:
        projects = list_all()
        if not projects: print("  No registered projects."); return
        print("\n  === Projects ===")
        for p in projects:
            marker = " <- active" if p["active"] else ""
            print(f"  {p['code']} - {p['name']} ({p['type']}, {p['dominan']}){marker}")
        print()

def cmd_setup_project(args):
    from .setup_project import analyze
    from .helpers import info
    try:
        res = analyze(args.path)
        verb = "Updated" if res["action"] == "updated" else "Registered"
        label = f"[{verb}] {res['code']}-{res['name']}"
        print(f"\n  {c(label, 'green')}")
        print(f"  Type: {res['type']} | Dominan: {res['dominan']}")
        print(f"  Stack: {', '.join(res['stack'])}")
        print(f"  Skills: {len(res['skills'])} matched")
        print(f"  Symlinks: .farewell/ injected in project\n")
    except ValueError as e:
        msg = f"[FAIL] {e}"
        print(f"  {c(msg, 'red')}")

def cmd_start_project(args):
    """Auto-detect current dir, register, inject symlinks."""
    from pathlib import Path
    from .setup_project import analyze
    from .helpers import info, fail
    path = args.path or str(Path.cwd())
    target = Path(path).resolve()
    print(f"\n  Scanning: {target}")
    from .setup_project import _probe_stack, _detect_type
    try:
        stack = _probe_stack(target)
        ptype = _detect_type(stack)
        dominan = _detect_dominan(ptype)
        info(f"Detected: {ptype} ({dominan}), stack={stack}")
        print(f"\n  Register project '{target.name}' as {ptype} ({dominan})? [Y/n] ", end="")
        try:
            resp = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            resp = "y"
        if resp in ("", "y", "yes"):
            res = analyze(str(target))
            label3 = f"[OK] {res['code']}-{res['name']} siap"
            print(f"\n  {c(label3, 'green')}")
            print(f"  Skills: {len(res['skills'])} matched")
            print(f"  Symlinks injected in {target}/.farewell/\n")
            from .sync import render as render_config
            render_config()
            write_context_footer()
        else:
            info("Cancelled")
    except Exception as e:
        fail(f"Error: {e}")

def _detect_dominan(ptype: str) -> str:
    m = {"flutter": "DART", "nextjs": "TYPESCRIPT", "react": "TYPESCRIPT",
         "vue": "JAVASCRIPT", "python": "PYTHON", "golang": "GOLANG",
         "rust": "RUST", "kotlin": "KOTLIN", "nodejs": "NODE"}
    return m.get(ptype, "UNKNOWN")

def cmd_org(args):
    from .org import chart, roles, workflow, priority
    if args.action in ("chart", "all"): chart()
    if args.action in ("roles", "all"): roles()
    if args.action in ("workflow", "all"): workflow()
    if args.action in ("priority", "all"): priority()

def cmd_cool(args):
    from .awesome_indexer import load_all, recommend
    from .state.registry import get_active, get_code
    from .indexer import get_skills
    from .helpers import info, ok
    plugs, themes, ags, projs, res = load_all()

    if args.action == "info" and args.query:
        q = args.query.lower()
        for cat, entries in [("plugin", plugs), ("theme", themes), ("agent", ags), ("project", projs)]:
            for e in entries:
                if q in e.get("name", "").lower():
                    name_val = e.get("name", "")
                    print(f"\n  {c(f'[{cat}] {name_val}', 'cyan')}")
                    print(f"  {e.get('tagline', '')}")
                    print(f"  {e.get('description', '')}")
                    print(f"  {e.get('repo', '')}\n")
                    return
        info(f"'{args.query}' not found")
    elif args.action == "search" and args.query:
        q = args.query.lower()
        found = []
        for cat, entries in [("plugin", plugs), ("theme", themes), ("agent", ags), ("project", projs)]:
            for e in entries:
                if q in e.get("name", "").lower() or q in e.get("tagline", "").lower():
                    found.append((cat, e))
        print(f"\n  {c(f'Found {len(found)} for: {args.query}', 'cyan')}\n")
        for cat, e in found[:20]:
            print(f"  [{cat:>7}] {e.get('name')} — {e.get('tagline', '')}")
    elif args.action == "recommend":
        active = get_active()
        code = get_code(active)
        skills = get_skills(code, active)
        stack = list(dict.fromkeys([s.split("-")[0] for s in skills if "-" in s]))
        if not stack: stack = [code.split("-")[0] if "-" in code else code]
        recs = recommend(stack)
        if recs:
            print(f"\n  {c(f'Recommendations for {code}-{active}', 'cyan')}\n")
            for r in recs[:5]:
                print(f"  - {r.get('name')}: {r.get('tagline', '')}")
                print(f"    {r.get('repo', '')}\n")
        else: print("  No recommendations\n")
    elif args.action == "stats":
        print(f"\n  {c('awesome-opencode', 'cyan')}")
        print(f"  plugins:  {len(plugs)}")
        print(f"  themes:   {len(themes)}")
        print(f"  agents:   {len(ags)}")
        print(f"  projects: {len(projs)}")
        print(f"  total:    {len(plugs)+len(themes)+len(ags)+len(projs)}\n")
    elif args.action == "list":
        cat = args.category or "all"
        for label, entries in [("plugin", plugs), ("theme", themes), ("agent", ags), ("project", projs)]:
            if cat in ("all", label):
                cnt = len(entries)
                print(f"\n  {c(f'{label}s ({cnt})', 'cyan')}")
                for e in entries[:10]:
                    print(f"    - {e.get('name')}")
                if cnt > 10: print(f"    ... +{cnt-10} more")
                print()

def cmd_run(args):
    from .dispatch import run
    run(args.task)

def cmd_memory(args):
    from .state.memory import memory_content, save_memory, user_content, save_user
    from .state.registry import get_active, get_code
    active = get_active()
    code = get_code(active)
    if args.action == "show":
        mem = memory_content(code, active)
        user = user_content(code, active)
        print(f"\n  {c('MEMORY.md', 'cyan')}")
        print(mem if mem else "  (empty)")
        print(f"\n  {c('USER.md', 'cyan')}")
        print(user if user else "  (empty)")
        print()
    elif args.action == "edit":
        import tempfile, subprocess, os
        content = memory_content(code, active) or "# MEMORY — project facts\n"
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
        f.write(content); f.close()
        editor = os.environ.get("EDITOR", "notepad")
        subprocess.call([editor, f.name])
        new_content = Path(f.name).read_text(encoding="utf-8")
        try:
            save_memory(code, active, new_content)
            print(f"  {c('[OK] MEMORY.md saved', 'green')}")
        except ValueError as e:
            msg2 = f"[FAIL] {e}"
            print(f"  {c(msg2, 'red')}")
        os.unlink(f.name)
    elif args.action == "save":
        target = args.target or "memory"
        content = " ".join(args.content) if args.content else ""
        if not content:
            print("  Usage: farewell-agent memory save --target memory|user \"content\"")
            return
        try:
            do_sync = not getattr(args, 'no_sync', False)
            if target == "user":
                save_user(code, active, content + "\n", sync_obsidian=do_sync)
            else:
                save_memory(code, active, content + "\n", sync_obsidian=do_sync)
            ok_label = f"[OK] {target.upper()}.md saved"
            print(f"  {c(ok_label, 'green')}")
            if do_sync:
                try:
                    from .obsidian import is_configured, vault_path
                    if is_configured(): info(f"Synced to Obsidian: {vault_path()}/{code}-{active}/")
                except: pass
        except ValueError as e:
            fail_msg = f"[FAIL] {e}"
            print(f"  {c(fail_msg, 'red')}")

def cmd_cost(args):
    from .cost import budget_status, recent_traces
    bs = budget_status()
    if args.action == "status":
        print(f"\n  {c('Budget', 'cyan')}")
        print(f"  Today: ${bs['spent_today']:.2f} / ${bs['daily_budget']:.2f}")
        print(f"  Month: ${bs['spent_month']:.2f} / ${bs['monthly_budget']:.2f}")
        pct_d = (bs['spent_today'] / bs['daily_budget'] * 100) if bs['daily_budget'] else 0
        pct_m = (bs['spent_month'] / bs['monthly_budget'] * 100) if bs['monthly_budget'] else 0
        if pct_d > 80: print(f"  {c(f'Warning: {pct_d:.0f}% daily budget used!', 'yellow')}")
        if pct_m > 80: print(f"  {c(f'Warning: {pct_m:.0f}% monthly budget used!', 'yellow')}")
        print(f"\n  {c('Recent Executions (trace-log.csv)', 'cyan')}")
        traces = recent_traces(5)
        if traces:
            for t in traces:
                icon = "✅" if t["success"] else "❌"
                print(f"  {icon} {t['project']} | {t['class']} | {t['agent']} | {t['summary'][:60]}")
        else:
            print("  (no traces yet — run a task first)")
        print()

def _get_team_label() -> str:
    f = config.FAREWELL_DIR / "team.json"
    if f.exists():
        t = json.loads(f.read_text(encoding="utf-8")).get("team", "TIM")
        return {"ON": "Divisi", "TIM": "Tim", "BAWAHAN": "Bawahan"}.get(t, "Tim")
    return "Tim"

def write_context_footer(project: str | None = None, mode: str | None = None):
    from .state.registry import get_active, get_code, list_all
    from .indexer import get_skills, write_active_skills
    from .awesome_indexer import recommend
    from .state.memory import get_context, memory_content, user_content
    from .cost import budget_status
    from .workmode import current as wm_current
    from .helpers import ok as _h_ok
    if project is None: project = get_active()
    if not project: project = "farewell-agent"
    if mode is None: mode = wm_current()
    code = get_code(project)
    if code == "???":
        code = "001"
    team = _get_team_label()
    skills = get_skills(code, project)
    sk = f" | Skills: {len(skills)}" if skills else ""
    of = f" | Mode: {mode.upper()}"

    write_active_skills(code, project)
    mem_ctx = get_context(code, project) if project else ""
    mem_text = memory_content(code, project) if project else ""
    user_text = user_content(code, project) if project else ""

    stack = list(dict.fromkeys([s.split("-")[0] for s in skills if "-" in s]))
    if stack:
        recs = recommend(stack)
        recs_str = "\n".join(f"  - {r.get('name')}: {r.get('tagline', '')}" for r in recs[:3])
        recs_block = f"\n\n# Awesome Recommendations\n{recs_str}" if recs_str else ""
    else:
        recs_block = ""

    budget = budget_status()
    bgt = f"${budget['spent_today']:.2f}/d ${budget['spent_month']:.2f}/m"
    mem_block = ""
    if mem_text:
        mem_block = f"\n\n# Project Memory\n{mem_text.strip()[:600]}"
    if user_text:
        mem_block += f"\n\n# User Profile\n{user_text.strip()[:400]}"

    ctx = f"""# State
Farewell: ON
Tier: {team}
Project: {code}-{project}{sk}{of} | Budget: {bgt}
{mem_ctx}{recs_block}{mem_block}
"""
    (config.STATE_DIR / "context.md").write_text(ctx, encoding="utf-8")

def main():
    # Write footer on startup
    write_context_footer()

    parser = argparse.ArgumentParser(
        prog="farewell-agent",
        description="AI coding assistant orchestrator — project-aware skills, memory, model routing"
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("workmode", help="Switch work mode")
    p.add_argument("action", nargs="?", default="status", choices=["plan", "build", "status"])
    p.set_defaults(func=cmd_workmode)

    p = sub.add_parser("team", help="Switch team tier")
    p.add_argument("action", nargs="?", default="status", choices=["divisi", "tim", "bawahan", "status"])
    p.set_defaults(func=cmd_team)

    p = sub.add_parser("status", help="Show state")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("setup", help="Clone dependencies: 9Router, ECC, awesome-opencode")
    p.set_defaults(func=cmd_setup)

    p = sub.add_parser("daily", help="Start 9Router + sync + readiness")
    p.set_defaults(func=cmd_daily)

    p = sub.add_parser("project", help="List / switch project")
    p.add_argument("action", nargs="?", default="list", choices=["switch", "list"])
    p.add_argument("code", nargs="?", default="", help="Project code (e.g. 002)")
    p.set_defaults(func=cmd_project)

    p = sub.add_parser("setup-project", help="Register & analyze a project")
    p.add_argument("path", help="Absolute path to project directory")
    p.set_defaults(func=cmd_setup_project)

    p = sub.add_parser("start-project", help="Auto-detect & register current dir")
    p.add_argument("path", nargs="?", default="", help="Optional path (default: CWD)")
    p.set_defaults(func=cmd_start_project)

    p = sub.add_parser("org", help="Show org hierarchy / roles / workflow")
    p.add_argument("action", nargs="?", default="all", choices=["chart", "roles", "workflow", "priority", "all"])
    p.set_defaults(func=cmd_org)

    p = sub.add_parser("cool", help="awesome-opencode: list / search / info / recommend / stats")
    p.add_argument("action", nargs="?", default="stats", choices=["list", "search", "info", "recommend", "stats"])
    p.add_argument("query", nargs="?", default="")
    p.add_argument("-c", "--category", default="all")
    p.set_defaults(func=cmd_cool)

    p = sub.add_parser("run", help="Run a task via OpenCode")
    p.add_argument("task", help="Task description")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("memory", help="View / edit MEMORY.md and USER.md")
    p.add_argument("action", choices=["show", "edit", "save"])
    p.add_argument("--target", choices=["memory", "user"], default="memory")
    p.add_argument("--no-sync", action="store_true", help="Skip Obsidian vault sync")
    p.add_argument("content", nargs="*", help="Content for save action")
    p.set_defaults(func=cmd_memory)

    p = sub.add_parser("cost", help="Token usage & budget")
    p.add_argument("action", nargs="?", default="status", choices=["status"])
    p.set_defaults(func=cmd_cost)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        import sys; sys.exit(1)
    args.func(args)
    write_context_footer()

if __name__ == "__main__":
    main()

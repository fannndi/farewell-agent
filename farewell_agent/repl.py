"""REPL mode — natural language input, auto-classify, execute, FOOTER, sync to Obsidian."""

from . import config
from .helpers import c, ok, info, fail
from .intent import classify_natural

SESSION_ID = None


def run():
    global SESSION_ID
    _init_session()

    print(f"\n  {c('Farewell Agent', 'cyan')}")
    print(f"  {c('='*40, 'cyan')}")
    print(f"  Ketik apapun. /help untuk bantuan. /keluar untuk selesai.\n")

    while True:
        try:
            text = _read_input()
            if not text:
                continue

            result = classify_natural(text)

            if result["intent"] == "exit":
                _exit_session()
                break

            elif result["intent"] == "help":
                _show_help()

            elif result["intent"] == "daily":
                _run_and_sync("daily", text, _exec_daily)

            elif result["intent"] == "setup_project":
                _run_and_sync("setup_project", text, _exec_setup_project, result)

            elif result["intent"] == "start_project":
                _run_and_sync("start_project", text, _exec_start_project)

            elif result["intent"] == "evolution":
                _run_and_sync("evolution", text, _exec_evolution)

            else:
                _run_and_sync("run", text, _exec_run, result)

        except KeyboardInterrupt:
            print(f"\n  {c('[EXIT]', 'yellow')} Sampai jumpa!")
            _exit_session()
            break


def _read_input() -> str:
    lines = []
    first = input(f"\n  {c('>', 'green')} ").strip()
    if not first:
        return ""
    if first.endswith("\\"):
        lines.append(first[:-1])
        while True:
            extra = input(f"  {c('...', 'green')} ").strip()
            if extra.endswith("\\"):
                lines.append(extra[:-1])
            else:
                lines.append(extra)
                break
    else:
        lines.append(first)
    return " ".join(lines)


def _run_and_sync(intent: str, raw: str, executor, result=None):
    from .state.registry import get_active, get_code
    from . import obsidian

    active = get_active()
    code = get_code(active)
    project = f"{code}-{active}"

    # Always consult vault before action
    from .context import lookup
    guide = lookup(raw)
    if guide:
        print(f"  {c('[Guide]', 'gray')} Buku panduan: artikel relevan ditemukan")

    # Execute
    output = executor(raw, result) if result else executor(raw)

    # FOOTER
    _show_footer(intent, project)

    # Sync to Obsidian
    _sync_to_obsidian(code, active, project, intent, raw, output)


def _exec_daily(raw: str) -> str:
    from .daily import run as daily_run
    daily_run()
    return "Daily selesai"


def _exec_setup_project(raw: str, result: dict) -> str:
    from .setup_project import analyze
    path = result.get("path", "")
    if not path:
        path = input(f"  {c('Path project:', 'yellow')} ").strip()
    if not path:
        return "Tidak ada path"
    res = analyze(path)
    msg = f"[OK] {res['code']}-{res['name']} siap"
    print(f"  {c(msg, 'green')}")
    return msg


def _exec_start_project(raw: str) -> str:
    from .setup_project import analyze
    from pathlib import Path
    path = str(Path.cwd())
    res = analyze(path)
    msg = f"[OK] {res['code']}-{res['name']} siap"
    print(f"  {c(msg, 'green')}")
    return msg


def _exec_evolution(raw: str) -> str:
    from .evolution import run as evo_run
    changes = evo_run()
    return "; ".join(changes) if changes else "Tidak ada perubahan"


def _exec_run(raw: str, result: dict) -> str:
    task = result.get("task", raw)
    wf = result.get("workflow")
    if wf:
        from .workflow import run_workflow
        run_workflow(wf, task)
    else:
        from .dispatch import run as dispatch_run
        dispatch_run(task)
    return "Selesai"


def _show_footer(intent: str, project: str):
    from .state.registry import get_active, get_code
    active = get_active()
    code = get_code(active)
    next_hints = {
        "run": "cek hasilnya atau lanjut task berikutnya",
        "daily": "tidak ada tindakan lanjutan",
        "setup_project": "mulai ngerjain project ini",
        "start_project": "ketik task untuk memulai",
        "evolution": "cek hasil evolusi di MEMORY.md",
    }
    hint = next_hints.get(intent, "lanjutkan")
    print(f"\n  {c('---', 'gray')}")
    print(f"  {c('### FOOTER', 'cyan')}")
    print(f"  Project: {project} | Session: {SESSION_ID or '-'}")
    print(f"  Next: {hint}")


def _sync_to_obsidian(code: str, name: str, project: str, intent: str, raw: str, output: str):
    try:
        from . import obsidian
        if not obsidian.is_configured():
            return
        now = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = (
            f"\n## {now}\n"
            f"- **User:** {raw[:200]}\n"
            f"- **Intent:** {intent}\n"
            f"- **Output:** {output[:300]}\n"
        )
        vault = obsidian._vault_path()
        if vault:
            proj_dir = vault / f"{code}-{name}"
            proj_dir.mkdir(parents=True, exist_ok=True)
            chat_file = proj_dir / "Chat-Log.md"
            with open(str(chat_file), "a", encoding="utf-8") as f:
                f.write(entry)
    except Exception:
        pass


def _init_session():
    global SESSION_ID
    from datetime import datetime
    SESSION_ID = f"repl-{datetime.now().strftime('%H%M%S')}"
    from .dispatch import _check_recovery
    _check_recovery()


def _exit_session():
    global SESSION_ID
    try:
        from .state.registry import get_active, get_code
        from .state.memory import save_session
        active = get_active()
        code = get_code(active)
        if active and code:
            save_session(code, active, f"REPL session {SESSION_ID} selesai")
        from . import obsidian as _obs
        if _obs.is_configured():
            _obs.write_session_note(code, active, "REPL session", "repl", "system", True,
                                     f"Session {SESSION_ID} completed")
    except Exception:
        pass
    print(f"\n  {c('Sampai jumpa!', 'cyan')}\n")


def _show_help():
    print(f"\n  {c('Cara Pakai Farewell Agent', 'cyan')}")
    print(f"  {c('='*40, 'cyan')}")
    print(f"  Cukup ketik apapun secara natural. Contoh:")
    print(f"    buat fitur login dengan flask")
    print(f"    perbaiki error di kalkulator")
    print(f"    cek kesehatan 9router")
    print(f"    update tools dan repo")
    print(f"    daftarin project flutter di C:\\path")
    print(f"    keluar")
    print(f"\n  Shortcut:")
    print(f"    /daily  - jalanin rutinitas harian")
    print(f"    /evolution - update tools + extract")
    print(f"    /help   - bantuan ini")
    print(f"    /keluar - selesai\n")

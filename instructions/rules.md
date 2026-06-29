# Farewell Rules

## Modes
- **PLAN**: read-only (Read/Glob/Grep only). No Bash write/edit.
- **BUILD**: full access. Orchestrator with team delegation.

## Golden Rule: Always Consult Buku Panduan

Sebelum EKSEKUSI APAPUN (run, workflow, audit, fix, dll):

1. **Cek Obsidian vault** — apakah ada artikel/skill yang relevan dengan task?
2. **Tampilkan ke user** — tunjukkin apa yang ditemukan dari buku panduan
3. **Inject ke prompt** — knowledge dari vault ditambahkan ke task description
4. **Baru eksekusi** — OpenCode jalan dengan konteks yang lebih kaya

Gunakan `farewell-agent cari <topik>` untuk mencari manual, atau `farewell-agent panduan` untuk lihat index.

## Memory System
- MEMORY.md: project facts, conventions, lessons (max 2,200 chars)
- USER.md: user preferences, skill level (max 1,375 chars)
- Both injected as frozen snapshot at session start
- Edit via `farewell-agent memory`

## Team Model Resolution
- `api-key.txt` defines model keys (LEADER_1, SPECIAL, WORKER, etc.)
- `roles.json` maps tier + task-override → model key
- Never hardcode model names in code

## Execution
- NEW task → HOLD → PLAN → APPROVE → execute
- Bug fix → langsung tanpa hold
- Commit only if asked

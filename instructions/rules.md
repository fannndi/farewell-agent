# Farewell Rules

## Modes
- **PLAN**: read-only (Read/Glob/Grep only). No Bash write/edit.
- **BUILD**: full access. Orchestrator delegates to read/write-only agents.

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

## Model Resolution
- `api-key.txt` defines model keys (LEADER_1, SPECIAL, WORKER, etc.)
- `roles.json` maps model key → role + agent (orchestrator/executor/planner)
- Strong read/write separation: orchestrator/planner = read-only, executor = write-only

## Execution
- NEW task → HOLD → PLAN → APPROVE → execute
- Bug fix → langsung tanpa hold
- Commit only if asked

## Obsidian Sync (WAJIB)
Setiap task selesai, WAJIB sinkron ke Obsidian vault:
1. Session-Log.md — catat task, agent, model, success, summary
2. MEMORY.md — update dengan pelajaran dari task ini
3. USER.md — update preferensi user jika ada perubahan

Gunakan `farewell_agent.obsidian` module untuk sync otomatis.
Jangan pernah lewatkan sync — Obsidian adalah sumber pengetahuan utama.

## Team Orchestration
- `team` agent = orkestrator (SPECIAL model) — delegasi, bukan eksekusi
- `senior-engineer` = eksekutor teknis (WORKER model)
- `director` = keputusan strategis (LEADER model)
- `junior-reviewer` = validasi kode (WORKER model)
- Team Leader JANGAN pernah ngerjain tugas sendiri. Selalu delegasi.

# Memory System

Inspired by [Hermes Agent](https://github.com/NousResearch/hermes-agent)'s dual-memory architecture + [Hermes Agent Self-Evolution](https://github.com/NousResearch/hermes-agent-self-evolution) trace-driven learning.

## Two Memory Files

Every project has two memory files in `.farewell/memory/{code}-{name}/`:

| File | Max Size | Purpose |
|------|----------|---------|
| **MEMORY.md** | 2,200 chars | Project facts, conventions, lessons learned |
| **USER.md** | 1,375 chars | User preferences, skill level, communication style |

## How It Works

### Frozen Snapshot Pattern

At the start of every session (when you run `farewell-agent run`):

1. MEMORY.md and USER.md are read from disk
2. They're injected into the context footer as a FROZEN block
3. The block does NOT change during the session — preserves prompt cache
4. If you update memory during a session, it saves to disk but appears in context NEXT session

### What To Save

**In MEMORY.md:**
- Environment facts: OS, tools, project structure
- Project conventions: coding style, architecture decisions
- Tool quirks and workarounds
- Completed tasks and lessons learned

**In USER.md:**
- Your name and role
- Communication preferences (terse vs detailed)
- Technical skill level
- Things to avoid / pet peeves

### Capacity Management

If MEMORY.md exceeds 2,200 chars, `farewell-agent memory save` returns an ERROR instead of silently truncating:

```
[FAIL] Memory too long (2300/2200 chars). Consolidate first.
```

This forces you (or the AI) to consolidate before adding new content.

## Auto-Consolidation (Self-Evolving Memory)

Setelah **setiap 5 task sukses**, farewell-agent otomatis nulis ringkasan ke MEMORY.md:

```
Task history (5 total, 4/1 success/fail):
- feature: 2/2 success
- fix: 2/1 success
```

Ini terinspirasi dari Hermes Self-Evolution pattern: execution trace → analysis → memory update.

## Session Lineage

Setiap `run` mencatat session lineage:

```json
{
  "sessions": [
    {
      "id": "001-project-1-143022",
      "parent": null,
      "task": "add login page",
      "agent": "build",
      "status": "completed",
      "summary": "Added login with email validation"
    },
    {
      "id": "001-project-2-150012",
      "parent": "001-project-1-143022",
      "task": "fix auth bug",
      "agent": "build",
      "status": "completed"
    }
  ]
}
```

### Resume Detection

Saat `run` lagi, otomatis detek session terakhir:

```
[Resume?] Previous session incomplete: fix auth bug (status: failed)
```

## Commands

```bash
# View both memory files
py -m farewell_agent memory show

# Edit with $EDITOR (Notepad by default on Windows)
py -m farewell_agent memory edit

# Quick save (+ auto-sync ke Obsidian)
py -m farewell_agent memory save "Flutter 3.24, Riverpod, GoRouter"

# Save ke user profile
py -m farewell_agent memory save --target user "User prefers concise examples"

# Skip Obsidian sync
py -m farewell_agent memory save "note" --no-sync

# Session history
py -m farewell_agent sessions list
py -m farewell_agent sessions insights
```

## Obsidian Vault Integration

Set `OBSIDIAN_VAULT` in `api-key.txt` to auto-sync memory to your Obsidian vault:

```
OBSIDIAN_VAULT=C:\Users\You\Documents\my-obsidian-vault
```

**What syncs automatically:**
- `MEMORY.md` → `{vault}/{code}-{name}/MEMORY.md`
- `USER.md` → `{vault}/{code}-{name}/USER.md`
- Session log → `{vault}/{code}-{name}/Session-Log.md` (append tiap `run`)

```bash
# Ekstrak semua pengetahuan dari 5 repo ke vault
py -m farewell_agent extract-knowledge

# Save + auto-sync to Obsidian (default)
py -m farewell_agent memory save "Flutter 3.24, Riverpod 2.5"

# Skip Obsidian sync
py -m farewell_agent memory save "quick note" --no-sync
```

## Execution Trace Log

Setiap `farewell-agent run` otomatis mencatat trace ke `.farewell/trace-log.csv`:

```
timestamp,project,task_class,agent,model,success,summary,duration_s
```

Ini adalah **eval dataset** untuk self-evolution (ala [Hermes Agent Self-Evolution](https://github.com/NousResearch/hermes-agent-self-evolution)) — foundation untuk auto-evolve skills berdasarkan pola pemakaian nyata.

```bash
py -m farewell_agent cost status  # lihat 5 trace terakhir
```

## Why Frozen Snapshot?

Hermes Agent proved that letting the system prompt change mid-session invalidates the LLM's prompt cache, increasing costs by ~75% per turn. By freezing memory at session start:

- **Cache stays warm** — system prompt prefix is cached across all turns
- **Memory still saves** — changes persist to disk immediately
- **Next session picks it up** — fresh snapshot with all updates

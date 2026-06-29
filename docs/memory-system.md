# Memory System

Inspired by [Hermes Agent](https://github.com/NousResearch/hermes-agent)'s dual-memory architecture.

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
- Technical skill level (this project assumes you're a beginner)
- Things to avoid / pet peeves

### Capacity Management

If MEMORY.md exceeds 2,200 chars, `farewell-agent memory save` returns an ERROR instead of silently truncating:

```
[FAIL] Memory too long (2300/2200 chars). Consolidate first.
```

This forces you (or the AI) to consolidate — merge related entries, remove stale ones — before adding new content.

## Commands

```bash
# View both memory files
py -m farewell_agent memory show

# Edit with $EDITOR (Notepad by default on Windows)
py -m farewell_agent memory edit

# Quick save
py -m farewell_agent memory save "This project uses Flutter 3.24 + Riverpod"
py -m farewell_agent memory save --target user "User prefers concise examples"
```

## Background Review (future)

After each `run` completes, a background review process can:
1. Analyze what was learned
2. Suggest MEMORY.md updates
3. Create custom skills in `.farewell/custom-skills/`

This is configured via `roles.json` and runs on the SPECIAL model (not the premium LEADER).

## Why Frozen Snapshot?

Hermes Agent proved that letting the system prompt change mid-session invalidates the LLM's prompt cache, increasing costs by ~75% per turn. By freezing memory at session start:

- **Cache stays warm** — system prompt prefix is cached across all turns
- **Memory still saves** — changes persist to disk immediately
- **Next session picks it up** — fresh snapshot with all updates

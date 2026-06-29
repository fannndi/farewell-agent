# Farewell Rules

## Modes
- **PLAN**: read-only (Read/Glob/Grep only). No Bash write/edit.
- **BUILD**: full access. Orchestrator with team delegation.

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

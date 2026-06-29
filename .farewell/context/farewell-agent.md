# farewell-agent

Type: Python CLI orchestrator
Stack: Python 3.10+ + OpenCode + ECC skills + awesome-opencode
Desc: AI coding assistant orchestrator. Manages skills per-project, session memory (MEMORY.md + USER.md), model routing via roles.json, and OpenCode dispatch.

## Key Directories
- `farewell_agent/` — source code
- `.farewell/` — per-project state (registry, manifests, memory)
- `docs/` — documentation
- `ecc/` — (cloned) ECC skill library
- `awesome-opencode/` — (cloned) awesome-opencode registry

## Command Flow
- `daily` → start 9Router, sync upstream, regenerate config, readiness check
- `run <task>` → classify intent → resolve model → dispatch to OpenCode
- `setup-project <path>` → detect stack, register, inject `.farewell/` symlinks
- `team [tier]` → switch model slot mapping (divisi/tim/bawahan)
- `workmode [plan/build]` → restrict or allow write access
- `memory [show/edit/save]` → manage per-project MEMORY.md and USER.md

## Memory Architecture
- MEMORY.md: max 2,200 chars, frozen snapshot per session
- USER.md: max 1,375 chars, user profile
- Session IDs tracked per project for `--continue` support
- Inspired by Hermes Agent's dual-memory system

## Model Resolution
- `roles.json` maps tier + task-override → role key
- `api-key.txt` maps role key → actual model/combo name
- 9Router combo names take priority over raw model names

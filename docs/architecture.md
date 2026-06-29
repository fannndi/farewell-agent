# Architecture

## Overview

Farewell Agent is an **orchestrator**, not an agent loop. It sits between you and OpenCode:

```
You ──→ farewell-agent ──→ OpenCode (opencode run) ──→ AI models
                  │
                  ├── roles.json (model resolution)
                  ├── api-key.txt (model config)
                  ├── MEMORY.md (project memory)
                  └── ECC skills (skill filtering)
```

## Design Principles

1. **Single source of truth** — Role/model resolution lives in `roles.json` + `api-key.txt`. Never hardcoded.
2. **Config generation = pure function** — `sync.py` renders `opencode.jsonc` from template + state. Called by `daily`, `team`, `workmode`.
3. **Provider-agnostic** — `router_client.py` provides `ModelProvider` interface. Swap 9Router ↔ DeepSeek-direct by changing config, not code.
4. **Frozen snapshot memory** — MEMORY.md injected at session start, never changes mid-session. Preserves prompt cache.

## Key Modules

| Module | Purpose |
|--------|---------|
| `cli.py` | Pure dispatcher — routes commands, zero business logic |
| `config.py` | Path constants |
| `state/io.py` | Atomic JSON read/write |
| `state/registry.py` | Project registry CRUD |
| `state/memory.py` | Session memory + MEMORY.md/USER.md management |
| `roles.py` | Role resolution — reads `roles.json` + `api-key.txt` |
| `sync.py` | Render `opencode.jsonc` from template |
| `team.py` | Switch team tier → triggers `sync.py` |
| `workmode.py` | Switch plan/build → triggers `sync.py` |
| `daily.py` | Orchestration: start 9Router, git sync, render config, readiness |
| `org.py` | View-only — reads from `roles.py` live |
| `intent.py` | Rule-based task classifier |
| `dispatch.py` | `opencode run` wrapper with session management |
| `setup_project.py` | Register project + inject `.farewell/` symlinks |
| `indexer.py` | Stack → ECC skill matching |
| `awesome_indexer.py` | awesome-opencode registry integration |
| `router_client.py` | ModelProvider interface |
| `cost.py` | Token usage tracking + budget |

## Data Flow: `run` command

```
1. intent.classify(task)          → task_class (security-review, deploy, or null)
2. roles.resolve_agent()          → agent name (build, security-reviewer, etc.)
3. roles.resolve_for_tier()       → resolved model (LEADER_1, SPECIAL, WORKER)
4. workmode.current()             → plan/build check
5. sync.render()                  → regenerate opencode.jsonc
6. dispatch: opencode run ...     → execute task via OpenCode
7. state/memory.save_session()    → save session ID + summary
8. write_context_footer()         → refresh .opencode/context.md
```

## Memory System

See `docs/memory-system.md` for detailed documentation on the Hermes-inspired dual-memory approach.

## Model Resolution

```
roles.json:  tier → {leader, special, worker_default, worker_pro}
             + task_overrides → security-review → worker_pro
api-key.txt: LEADER_1=ocg/deepseek-v4-flash
             SPECIAL=oc/deepseek-v4-flash-free
             WORKER=oc/mimo-v2.5-free

Resolve: tier(task_overrides) → role_key → api-key.txt value → combo name (9Router alias) or raw model
```

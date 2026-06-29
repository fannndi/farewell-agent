# Architecture

## Overview

Farewell Agent is an **orchestrator** with a **learning loop**. It sits between you and OpenCode, routing tasks, managing memory, consulting knowledge, and learning from results.

```
You ──→ farewell-agent ──→ OpenCode (opencode run) ──→ AI models
                  │                      │
                  │ 1. Buku Panduan       │ 6. Execution trace
                  │    (Obsidian vault)   │    (trace-log.csv)
                  │ 2. Intent classify    │ 7. Learning loop
                  │ 3. Session tracking   │    (patterns.json)
                  │ 4. Model resolution   │ 8. Memory consolidation
                  │ 5. Dispatch           │
```

## Design Principles

1. **Single source of truth** — Role/model resolution in `roles.json` + `api-key.txt`. Never hardcoded.
2. **Config generation = pure function** — `sync.py` renders `opencode.jsonc`. Called by `daily`, `team`, `workmode`.
3. **Buku Panduan first** — Before ANY execution, consult Obsidian vault for relevant knowledge.
4. **Frozen snapshot memory** — MEMORY.md injected at session start, never changes mid-session.
5. **Self-evolving** — Every task leaves a trace → pattern analyzed → memory auto-consolidated → skills improved.

## Key Modules

| Module | Purpose |
|--------|---------|
| `cli.py` | Pure dispatcher — routes commands, zero business logic |
| `config.py` | Path constants |
| `sync.py` | Render `opencode.jsonc` from template + state |
| `roles.py` | Role resolution — reads `roles.json` + `api-key.txt` |
| `intent.py` | Rule-based classifer — workflows + task types (Indo + English) |
| `context.py` | Knowledge-aware context enricher — searches Obsidian vault |
| `guide.py` | Guide book (buku panduan) — search, index, status |
| `workflow.py` | Multi-step orchestrator — audit, feature, fix, learn, health, refactor |
| `dispatch.py` | `opencode run` wrapper + session mgmt + learning loop |
| `learn.py` | Post-task analysis, pattern tracking, auto-memory consolidation |
| `team.py` | Switch team tier → triggers `sync.py` |
| `workmode.py` | Switch plan/build → triggers `sync.py` |
| `daily.py` | Orchestration: start 9Router, git sync, render config, readiness |
| `setup_project.py` | Register project + inject `.farewell/` symlinks |
| `indexer.py` | Stack → ECC skill matching |
| `awesome_indexer.py` | awesome-opencode registry |
| `cost.py` | Token/budget tracking + execution trace log |
| `obsidian.py` | Obsidian vault sync (MEMORY.md + session notes) |
| `router_client.py` | ModelProvider interface |
| `org.py` | View-only org hierarchy — reads from `roles.py` live |
| `helpers.py` | Colors & formatting |
| `state/io.py` | Atomic JSON read/write |
| `state/registry.py` | Project registry CRUD |
| `state/memory.py` | MEMORY.md / USER.md per-project management |
| `state/session.py` | Session continuity — lineage tracking, resume detection |

## Data Flow: `run` command

```
1. intent.classify(task)           → (workflow, task_class)
   │                                → workflow="feature" → workflow.py handles it
   │                                → task_class="security-review" → dispatch.py handles it
   │
2. context.lookup(task)             → search Obsidian vault for relevant knowledge
   │                                → inject as context block into prompt
   │
3. state.session.start_session()    → track lineage (parent/child chain)
   │
4. roles.resolve_agent()            → agent name (build, security-reviewer, etc.)
   roles.resolve_for_tier()         → resolved model (LEADER_1, SPECIAL, WORKER)
   workmode.current()               → plan/build guard
   │
5. sync.render()                    → regenerate opencode.jsonc
   │
6. dispatch: opencode run ...       → execute task via OpenCode
   │
7. state.session.end_session()      → mark complete/failed
   cost.write_trace()               → append to trace-log.csv
   learn.analyze_completion()       → track patterns, auto-consolidate memory
   obsidian.write_session_note()    → log to vault Session-Log.md
   │
8. write_context_footer()           → refresh .opencode/context.md
```

## Self-Evolution Loop

```
setiap run ──→ trace-log.csv (execution trace)
                  │
                  ▼
            patterns.json (success/fail by class)
                  │
                  ├── setiap 5 success → auto-consolidate MEMORY.md
                  │
                  ├── insights → farewell-agent sessions insights
                  │
                  └── future: DSPy + GEPA skill evolution
```

Trace-log.csv format (Hermes Self-Evolution pattern):

```
timestamp,project,task_class,agent,model,success,summary,duration_s
```

## Model Resolution

```
roles.json:  tier → {leader, special, worker_default, worker_pro}
             + task_overrides → security-review → worker_pro
             + agent_map → security-review → security-reviewer
             + plan_agents → [team, planner, docs-lookup]

api-key.txt: LEADER_1=ocg/deepseek-v4-flash
             SPECIAL=oc/deepseek-v4-flash-free
             WORKER=oc/mimo-v2.5-free

Alur: task_class → task_overrides → tier → role_key → api-key.txt
      → combo name (9Router alias) or raw model ID
```

## Knowledge Sources

| Source | Files | Extracted to Obsidian |
|--------|-------|----------------------|
| ECC | 271 skills | 122 files, categorized |
| awesome-opencode | 212 entries | 1 file (awesome-opencode.md) |
| 9Router | — | 1 file (9router.md) + active combos |
| Hermes Agent | 5,734 files | 1 file (hermes-agent.md) |
| Hermes Self-Evolution | 30 files | 1 file (hermes-self-evolution.md) |

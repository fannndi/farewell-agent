# Command Reference

```
farewell-agent

Usage:
  farewel-agent setup
  farewel-agent daily
  farewel-agent run "<task>"

  # Natural workflows
  farewel-agent audit [fokus]
  farewel-agent feature "<desc>"
  farewel-agent fix "<bug>"
  farewel-agent learn "<topic>"
  farewel-agent health
  farewel-agent refactor [fokus]

  # Management
  farewel-agent workmode [plan|build|status]
  farewel-agent team [divisi|tim|bawahan|status]
  farewel-agent status
  farewel-agent project [list|switch <code>]
  farewel-agent setup-project <path>
  farewel-agent start-project [<path>]

  # Knowledge
  farewel-agent cari <query>
  farewel-agent panduan [index|status]
  farewel-agent extract-knowledge

  # Memory & Sessions
  farewel-agent memory [show|edit|save]
  farewel-agent sessions [list|insights]

  # Info
  farewel-agent org [chart|roles|workflow|priority|all]
  farewel-agent cool [list|search|recommend|stats]
  farewel-agent cost [status]
```

## Core Commands

### `setup`
Clone semua dependencies (9Router, ECC, awesome-opencode, Hermes Agent, Hermes Self-Evolution).

```
py -m farewell_agent setup
```

### `daily`
Start 9Router, sync upstream, regenerate config, readiness report. Satu command buat siap kerja.

```
py -m farewell_agent daily
```

### `run`
Single entry point untuk task execution. Otomatis:
1. Cari buku panduan (Obsidian vault) untuk knowledge relevan
2. Classify intent (workflow + task type)
3. Resolve model/agent
4. Execute via OpenCode
5. Trace + learning loop + auto-consolidate memory

```
py -m farewell_agent run "add authentication middleware"
py -m farewell_agent run "fix date parsing bug"
py -m farewell_agent run "audit security vulnerabilities"
py -m farewell_agent run "perbaiki bug tanggal"
py -m farewell_agent run "tambah fitur login page"
```

## Natural Workflow Commands

Tidak perlu hafal command — cukup bilang apa yang kamu mau.

### `audit`
Project audit: otomatis switch ke plan mode, jalanin code-reviewer + security-reviewer, generate report.

```
py -m farewell_agent audit
py -m farewell_agent audit "bagian auth"
py -m farewell_agent run "audit project ini"
```

### `feature`
Feature development workflow: plan → implement → review.

```
py -m farewell_agent feature "login page with email and password"
py -m farewell_agent feature "payment gateway integration"
py -m farewell_agent run "tambah fitur export PDF"
```

### `fix`
Bug fix workflow: diagnose → fix → verify.

```
py -m farewell_agent fix "login ga bisa"
py -m farewell_agent fix "build error flutter"
py -m farewell_agent run "perbaiki bug tanggal"
py -m farewell_agent run "ga jalan auth"
```

### `learn`
Research mode: otomatis switch ke plan mode, jalanin docs-lookup/planner agent.

```
py -m farewell_agent learn "flutter riverpod state management"
py -m farewell_agent learn "docker compose postgresql"
py -m farewell_agent run "belajar rust lifetime"
```

### `health`
System health check — sama seperti `daily`.

```
py -m farewell_agent health
py -m farewell_agent run "cek kesehatan"
```

### `refactor`
Code cleanup: dead code, unused imports, redundant structure.

```
py -m farewell_agent refactor
py -m farewell_agent refactor "utils directory"
py -m farewell_agent run "rapihin kode"
```

## Guide Book / Knowledge

### `cari`
Search the Obsidian vault for relevant skills and knowledge.

```
py -m farewell_agent cari docker
py -m farewell_agent cari flutter riverpod
py -m farewell_agent cari rust pattern
```

### `panduan`
Open the guide book index or check vault status.

```
py -m farewell_agent panduan        # Show index
py -m farewell_agent panduan status # Show vault stats
```

### `extract-knowledge`
Extract all knowledge from 5 repos (ECC, awesome-opencode, 9Router, Hermes Agent, Hermes Self-Evolution) into the Obsidian vault.

```
py -m farewell_agent extract-knowledge
```

## Management Commands

### `project`
List or switch active project.

```
py -m farewell_agent project            # List all projects
py -m farewell_agent project switch 002 # Switch to project 002
py -m farewell_agent project 002        # Shortcut (same)
```

### `setup-project`
Register a project, detect stack, inject `.farewell/` symlinks.

```
py -m farewell_agent setup-project C:\Users\You\Documents\my-project
```

### `start-project`
Auto-detect current directory, show detection, confirm, and register.

```
cd C:\Users\You\Documents\my-project
py -m C:\path\to\farewell-agent -m farewel-agent start-project
```

### `team`
Switch between 3 model tiers.

```
py -m farewell_agent team divisi     # Premium: LEADER_1 model
py -m farewell_agent team tim        # Default: SPECIAL (balanced)
py -m farewell_agent team bawahan    # Economical: WORKER only
```

### `workmode`
Switch between read-only (PLAN) and full-access (BUILD).

```
py -m farewell_agent workmode plan   # Read-only — research, planning
py -m farewell_agent workmode build  # Full access — execution
```

## Memory & Sessions

### `memory`
View, edit, or save MEMORY.md and USER.md. Auto-sync to Obsidian vault jika dikonfigurasi.

```
py -m farewell_agent memory show
py -m farewell_agent memory edit                    # Opens $EDITOR
py -m farewell_agent memory save "Flutter 3.24, Riverpod 2.5"
py -m farewell_agent memory save --target user "Aku pemula, jelasin step by step"
py -m farewell_agent memory save "note" --no-sync   # Skip Obsidian
```

### `sessions`
View session history, task patterns, and insights.

```
py -m farewell_agent sessions list      # 10 session terakhir
py -m farewell_agent sessions insights  # Success rate + pola
```

## Info Commands

### `status`
One-line summary: project, mode, team, skill count, budget, insights.

```
py -m farewell_agent status
# -> 001-farewell-agent | BUILD | Skills: 14 | Budget: $0.00/day | 5 tasks run (80% success) | Tim
```

### `cost`
Token usage, budget, and execution traces.

```
py -m farewell_agent cost status
# -> Budget + 5 trace terakhir (timestamp, project, class, agent, status)
```

### `org`
Display organization hierarchy with live model resolution.

```
py -m farewell_agent org          # Show all
py -m farewell_agent org chart
py -m farewell_agent org roles
py -m farewell_agent org workflow
py -m farewell_agent org priority
```

### `cool`
Browse awesome-opencode registry.

```
py -m farewell_agent cool stats
py -m farewell_agent cool list
py -m farewell_agent cool search "flutter"
py -m farewell_agent cool recommend
```

## Error Handling

When a task fails, farewell-agent:
1. Mencatat trace ke `trace-log.csv` dengan detail error
2. Menandai session sebagai "failed"
3. Learning loop mencatat pola kegagalan
4. Otomatis suggest solusi (ganti tier, cek 9Router, dll)

Cek riwayat:

```
py -m farewell_agent sessions list
py -m farewell_agent sessions insights
```

# Farewell Agent

**Your AI coding assistant orchestrator.**

Satu tool untuk ngatur skill, memory, model routing — tinggal bilang "fix bug", "audit project", "tambah fitur", sisanya diurus.

```
┌──────────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  You                 │     │  farewell-agent   │     │   OpenCode    │
│  "fix auth bug" ─────┼──▶  │  ───────────────  │──▶  │  ──────────   │
│                      │     │  cari buku →      │     │  execute task │
│  "audit project" ────┼──▶  │  classify → route │     │  return result│
│                      │     │  → dispatch →     │     └──────────────┘
│  "tambah fitur" ─────┼──▶  │  → learn → save   │
└──────────────────────┘     └──────────────────┘
```

## Kenapa Farewell Agent?

- **Bahasa sehari-hari** — "audit project", "tambah fitur", "cek kesehatan", "belajar flutter". Gak perlu hafal command.
- **Punya buku panduan** — Obsidian vault jadi knowledge base. Tiap jalan, dicek dulu, inject knowledge relevan.
- **Proyek aware** — register project, paham stack-nya, inject skill yang relevan.
- **Memory per project** — inget konteks, preferensi, keputusan teknis. Kaya Hermes Agent.
- **Self-evolving** — trace tiap task dicatat, pola dianalisis, memory auto-consolidate.
- **Hemat token** — 271 ECC skills difilter jadi ~10-20 per project.

## Quick Install

```bash
# Clone
git clone https://github.com/fannndi/farewell-agent.git
cd farewell-agent

# Install Python deps
pip install pyyaml

# Clone dependencies (9Router, ECC, awesome-opencode, Hermes Agent)
py -m farewell_agent setup

# Copy config contoh
cp .api-key.example.txt api-key.txt
# Edit api-key.txt — isi model keys + optional OBSIDIAN_VAULT
```

### Contoh `api-key.txt`

```
NINEROUTER_API_KEY=sk-your-9router-key
LEADER_1=ocg/deepseek-v4-flash
SPECIAL=oc/deepseek-v4-flash-free
WORKER=oc/mimo-v2.5-free
WORKER_PRO=ocg/deepseek-v4-flash
OBSIDIAN_VAULT=C:\Users\You\Documents\obsidian-vault
```

## Quick Start

```bash
# 1. Daily readiness
py -m farewell_agent daily

# 2. Register project (auto-detect CWD)
cd C:\Users\You\Documents\my-project
py -m C:\path\to\farewell-agent -m farewell_agent start-project

# 3. Ekstrak knowledge ke Obsidian (kalau OBSIDIAN_VAULT diset)
py -m farewell_agent extract-knowledge

# 4. Jalanin task
py -m farewell_agent run "add login page with email and password"
```

## Everyday Usage — Contoh Nyata

### Kerja harian — tinggal bilang

```bash
# Perbaiki error
py -m farewell_agent fix "ga jalan auth"
py -m farewell_agent fix "build error flutter"
py -m farewell_agent run "perbaiki bug tanggal"

# Tambah fitur baru
py -m farewell_agent feature "login page with email"
py -m farewell_agent run "tambah fitur payment gateway"

# Audit project
py -m farewell_agent audit
py -m farewell_agent audit "bagian keamanan"

# Belajar / riset
py -m farewell_agent learn "flutter riverpod"
py -m farewell_agent run "belajar docker compose"

# Cek kesehatan system
py -m farewell_agent health
py -m farewell_agent run "cek kesehatan"

# Rapihin kode
py -m farewell_agent refactor
```

### Cari pengetahuan di buku panduan (Obsidian vault)

```bash
py -m farewell_agent cari docker flutter
py -m farewell_agent cari rust deployment
py -m farewell_agent panduan
py -m farewell_agent panduan status
```

### Manajemen project

```bash
# Daftar project
py -m farewell_agent project

# Switch project
py -m farewell_agent project 002

# Register project baru
py -m farewell_agent setup-project C:\Users\You\Documents\proyek-baru
```

### Memory & session

```bash
# Simpen catatan project
py -m farewell_agent memory save "Flutter 3.24, Riverpod 2.5, GoRouter 14"
py -m farewell_agent memory save --target user "Aku pemula, jelasin step by step"
py -m farewell_agent memory save "note rahasia" --no-sync

# Lihat session history
py -m farewell_agent sessions list
py -m farewell_agent sessions insights

# Lihat budget + trace
py -m farewell_agent cost status
```

### Model routing

```bash
py -m farewell_agent team divisi     # Premium: LEADER model
py -m farewell_agent team tim        # Default: SPECIAL (balanced)
py -m farewell_agent team bawahan    # Economical: WORKER only

py -m farewell_agent workmode plan   # Read-only (riset)
py -m farewell_agent workmode build  # Full access (eksekusi)
```

## Commands at a Glance

| Command | Fungsi |
|---------|--------|
| `setup` | Clone dependencies (9Router, ECC, awesome, Hermes) |
| `daily` | Start 9Router + sync upstream + readiness check |
| `run "<task>"` | Classify → cari buku panduan → route → OpenCode → learn |
| `audit [fokus]` | Audit project: code review + security check |
| `feature "<desc>"` | Tambah fitur: plan → implement → review |
| `fix "<bug>"` | Perbaiki bug: diagnose → fix → verify |
| `learn "<topic>"` | Riset: plan mode → research docs |
| `health` | System health check (9Router, config, dependencies) |
| `refactor [fokus]` | Bersihin kode: dead code, imports, structure |
| `cari <query>` | Cari pengetahuan di Obsidian vault |
| `panduan [status]` | Buka buku panduan / cek status |
| `setup-project <path>` | Register project + inject `.farewell/` symlinks |
| `start-project [path]` | Auto-detect CWD → register (dengan konfirmasi) |
| `project [list\|switch <code>]` | List / switch project |
| `team [divisi\|tim\|bawahan]` | Switch model tier |
| `workmode [plan\|build]` | Read-only / full access |
| `memory [show\|edit\|save]` | Manage MEMORY.md + USER.md (+ Obsidian sync) |
| `sessions [list\|insights]` | Session history + success rate + pola |
| `cost status` | Budget + execution trace |
| `extract-knowledge` | Ekstrak knowledge dari 5 repo ke Obsidian vault |
| `org [chart\|roles\|workflow]` | Org hierarchy + decision priority |

## Alur Kerja: `run`

```
Anda: "tambah fitur login page"

  1. [?] Membuka buku panduan...
     → Cari skill/knowledge relevan di Obsidian vault
     → Inject sebagai konteks ke prompt

  2. Intent classify → workflow='feature', task_class=null

  3. Session start → lineage tracking

  4. OpenCode run → eksekusi via agent yang tepat

  5. ✅ Done (28s)

  6. Learning loop:
     → Trace dicatat (trace-log.csv)
     → Pattern dianalisis (patterns.json)
     → Memory auto-consolidate tiap 5 task
     → Saran: "First 'feature' task — catat workflow ke MEMORY.md"
```

## Project Structure

```
farewell-agent/
├── farewell_agent/          # Source code (20 modules)
│   ├── cli.py               # Dispatcher (command -> module)
│   ├── config.py            # Paths
│   ├── roles.py             # Role/model resolution
│   ├── sync.py              # Render opencode.jsonc
│   ├── daily.py             # Orchestration
│   ├── team.py              # Team tier switch
│   ├── workmode.py          # Plan/build switch
│   ├── dispatch.py          # opencode run wrapper + learning loop
│   ├── workflow.py          # Multi-step workflow orchestrator
│   ├── intent.py            # Task classifier (Indo + English)
│   ├── context.py           # Knowledge-aware context enricher
│   ├── guide.py             # Guide book (buku panduan) search
│   ├── learn.py             # Post-task analysis + auto-consolidation
│   ├── session.py           # Session continuity + lineage
│   ├── setup_project.py     # Project registration + symlink
│   ├── indexer.py           # Skill matching
│   ├── awesome_indexer.py   # awesome-opencode
│   ├── router_client.py     # Provider interface
│   ├── cost.py              # Budget + execution trace log
│   ├── obsidian.py          # Obsidian vault sync
│   ├── org.py               # Org hierarchy display
│   ├── helpers.py           # Colors & formatting
│   └── state/
│       ├── io.py            # JSON read/write
│       ├── registry.py      # Project registry
│       ├── memory.py        # MEMORY.md + USER.md + session
│       └── session.py       # Session lineage tracking
├── ecc/                     # 271 skills (cloned, gitignored)
├── 9router/                 # LLM Router (cloned, gitignored)
├── awesome-opencode/        # 212 registry entries (cloned, gitignored)
├── hermes-agent/            # 5,734 files, 205k stars (cloned, gitignored)
├── hermes-agent-self-evolution/  # 4.4k stars (cloned, gitignored)
├── docs/                    # Documentation
├── instructions/            # Rules + Buku Panduan golden rule
├── scripts/                 # extract_knowledge.py
└── .farewell/               # State files (roles, custom-skills, memory)
```

## Learn More

- [Getting Started](docs/getting-started.md) — step-by-step
- [Commands](docs/commands.md) — all commands with examples
- [Project Setup](docs/project-setup.md) — register + symlink injection
- [Memory System](docs/memory-system.md) — MEMORY.md, USER.md, session lineage
- [Architecture](docs/architecture.md) — module map + data flow

### Inspirasi

- **[Hermes Agent](https://github.com/NousResearch/hermes-agent)** (205k ⭐) — memory system, session lineage, self-improving loop
- **[Hermes Agent Self-Evolution](https://github.com/NousResearch/hermes-agent-self-evolution)** (4.4k ⭐) — DSPy + GEPA skill optimization
- **[ECC](https://github.com/affaan-m/ECC)** — 271 skill library
- **[9Router](https://github.com/decolua/9router)** — LLM routing/proxy
- **[awesome-opencode](https://github.com/awesome-opencode/awesome-opencode)** — plugin/agent registry

# Farewell Agent

**Your AI coding assistant orchestrator.**

Satu tool untuk ngatur skill, memory, model routing — biar kamu tinggal bilang "fix bug" doang, sisanya diurus.

```
┌──────────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  You                 │     │  farewell-agent   │     │   OpenCode    │
│  "fix auth bug" ─────┼──▶  │  ───────────────  │──▶  │  ──────────   │
│                      │     │  classify → route │     │  execute task │
│  Py -m farewell_agent│     │  → dispatch       │     │  return result│
└──────────────────────┘     └──────────────────┘     └──────────────┘
```

## Kenapa Farewell Agent?

- **Gak perlu hapal** — gak perlu tau team tier, model name, skill count. Tinggal bilang mau ngapain.
- **Proyek aware** — register project, dia paham stack-nya, inject skill yang relevan.
- **Memory per project** — inget konteks, preferensi kamu, keputusan teknis. Kaya Hermes Agent tapi simpel.
- **Hemat token** — 271 ECC skills difilter jadi ~10-20 per project. Model mahal cuma dipake kalo perlu.
- **Satu command** — `farewell-agent run "task"` doang, start-to-finish.

## Quick Install

```bash
# Clone
git clone https://github.com/fannndi/farewell-agent.git
cd farewell-agent

# Install deps
pip install pyyaml

# Copy config contoh
cp .api-key.example.txt api-key.txt
# Edit api-key.txt — isi model keys kamu (contoh di bawah)
```

### Contoh `api-key.txt`

```
NINEROUTER_API_KEY=sk-your-9router-key
LEADER_1=ocg/deepseek-v4-flash
SPECIAL=oc/deepseek-v4-flash-free
WORKER=oc/mimo-v2.5-free
WORKER_PRO=ocg/deepseek-v4-flash
```

## Quick Start

```bash
# 1. Daily readiness (start 9Router + sync + config)
py -m farewell_agent daily

# 2. Register project kamu
py -m farewell_agent setup-project C:\Users\You\Documents\my-project

# 3. Jalanin task
py -m farewell_agent run "add login page with email and password"
```

> Ganti `my-project` dengan path project kamu yang bener. Nama project/model gak hardcode.

## Everyday Usage

```bash
# Mulai hari — sekali aja
py -m farewell_agent daily

# Kerja — tinggal bilang
py -m farewell_agent run "fix the date parsing bug"
py -m farewell_agent run "add error handling to API routes"
py -m farewell_agent run "audit security vulnerabilities"

# Ganti project — tinggal kode
py -m farewell_agent project 002
py -m farewell_agent run "refactor the auth service"

# Simpen memori (auto-sync ke Obsidian kalau api-key.txt punya OBSIDIAN_VAULT)
py -m farewell_agent memory save "This project uses Riverpod 2.5 + GoRouter"
py -m farewell_agent memory save --target user "Aku pemula, jelasin step by step"
py -m farewell_agent memory save "note rahasia" --no-sync  # skip Obsidian

# Cek status + budget + trace terakhir
py -m farewell_agent status
py -m farewell_agent cost status
```

## Commands at a Glance

| Command | Fungsi |
|---------|--------|
| `daily` | Start 9Router + sync upstream + readiness |
| `run "<task>"` | **Entry point utama** — classify → route → execute |
| `setup-project <path>` | Register project + inject `.farewell/` |
| `start-project [path]` | Auto-detect CWD → register |
| `project [list\|switch <code>]` | List/switch project |
| `team [divisi\|tim\|bawahan]` | Switch model tier |
| `workmode [plan\|build]` | Read-only / full access |
| `memory [show\|edit\|save]` | Manage project memory (+ Obsidian sync) |
| `cost status` | Cek budget + trace eksekusi terakhir |
| `org [chart\|roles\|workflow]` | Show AI org hierarchy |
| `cool [list\|search\|recommend]` | Browse awesome-opencode |
| `cost status` | Cek budget token |

## Project Structure

```
farewell-agent/
├── farewell_agent/        # Source code
│   ├── cli.py             # Dispatcher (command → module)
│   ├── config.py          # Paths
│   ├── roles.py           # Role/model resolution
│   ├── sync.py            # Render opencode.jsonc
│   ├── daily.py           # Orchestration
│   ├── team.py            # Team tier switch
│   ├── workmode.py        # Plan/build switch
│   ├── dispatch.py        # opencode run wrapper
│   ├── intent.py          # Task classifier
│   ├── setup_project.py   # Project registration
│   ├── indexer.py         # Skill matching
│   ├── awesome_indexer.py # awesome-opencode
│   ├── router_client.py   # Provider interface
│   ├── cost.py            # Budget tracking + execution trace log
│   ├── obsidian.py        # Obsidian vault sync
│   ├── org.py             # Org hierarchy display
│   ├── helpers.py         # Colors & formatting
│   └── state/
│       ├── io.py          # JSON read/write
│       ├── registry.py    # Project registry
│       └── memory.py      # MEMORY.md + session
├── docs/                  # 📚 Documentation
├── instructions/          # Rules
├── .farewell/             # State files
│   ├── roles.json         # Tier + task override config
│   ├── context/           # Per-project context
│   └── custom-skills/     # User-created skills
└── pyproject.toml
```

## Learn More

- [Getting Started](docs/getting-started.md) — step-by-step first run
- [Commands](docs/commands.md) — all commands
- [Project Setup](docs/project-setup.md) — register + symlink
- [Memory System](docs/memory-system.md) — MEMORY.md + USER.md
- [Architecture](docs/architecture.md) — how it works

### Hermes Agent Inspiration

Memory system inspired by [Hermes Agent](https://github.com/NousResearch/hermes-agent) (Nous Research, 205k ⭐):
- Dual memory (MEMORY.md + USER.md) with strict char limits
- Frozen snapshot injection for prompt cache efficiency
- Self-improving loop via background review
- Provider-agnostic model resolution

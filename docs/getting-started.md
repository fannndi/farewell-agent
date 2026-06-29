# Getting Started

## Prerequisites

- Python 3.10+
- OpenCode (`opencode run` — install from [opencode.ai](https://opencode.ai))
- 9Router (Node.js, port 20128) — auto-installed via `setup`
- Git (for cloning dependencies)
- Obsidian (optional — for knowledge base / buku panduan)

## Installation

```bash
# Clone repo
git clone https://github.com/fannndi/farewell-agent.git
cd farewell-agent

# Install Python dependencies
pip install pyyaml
```

## Quick Start — First Time

### 0. Clone dependencies

```bash
py -m farewell_agent setup
```

Ini clone 5 repo penting:
- **9Router** — LLM routing/proxy
- **ECC** — 271 skill library
- **awesome-opencode** — 212 plugin/agent/project entries
- **Hermes Agent** (205k stars) — self-improving AI agent
- **Hermes Self-Evolution** (4.4k stars) — DSPy + GEPA optimization

### 1. Prepare config

```bash
cp .api-key.example.txt api-key.txt
```

Edit `api-key.txt` — isi model keys kamu:

```
NINEROUTER_API_KEY=sk-your-key
LEADER_1=ocg/deepseek-v4-flash
SPECIAL=oc/deepseek-v4-flash-free
WORKER=oc/mimo-v2.5-free
WORKER_PRO=ocg/deepseek-v4-flash
# Optional: buat sync ke Obsidian vault
OBSIDIAN_VAULT=C:\Users\You\Documents\obsidian-vault
```

### 2. Setup Obsidian (optional)

Kalau punya Obsidian vault, set `OBSIDIAN_VAULT` di `api-key.txt`, lalu:

```bash
# Ekstrak knowledge dari 5 repo ke vault
py -m farewell_agent extract-knowledge

# Cek hasilnya
py -m farewell_agent panduan
py -m farewell_agent cari flutter
```

### 3. Run your first daily

```bash
py -m farewell_agent daily
```

Ini otomatis: start 9Router → sync ECC/awesome → regenerate config → readiness report.

### 4. Register your project

```bash
cd C:\Users\You\Documents\my-project
py -m C:\path\to\farewell-agent -m farewell_agent start-project
```

Atau dengan path eksplisit:

```bash
py -m farewell_agent setup-project C:\Users\You\Documents\my-project
```

### 5. Jalanin task pertama

```bash
# Cara simpel — farewell-agent otomatis detek intent
py -m farewell_agent run "add login page with email and password"

# Atau pake workflow command
py -m farewell_agent feature "login page with email and password"
```

## Daily Workflow

Setelah setup, tiap hari cukup:

```bash
py -m farewell_agent daily
py -m farewell_agent run "continue working on [task]"
```

## Contoh Cepat

```bash
# Indonesia — farewell-agent paham
py -m farewell_agent run "perbaiki bug tanggal di laporan"
py -m farewell_agent run "tambah fitur export PDF"
py -m farewell_agent run "cek kesehatan system"
py -m farewell_agent run "belajar riverpod flutter"

# Inggris
py -m farewell_agent run "fix date parsing in report module"
py -m farewell_agent run "add export to PDF feature"
```

## Tips

- **Gak tau mau ngapain?** — `py -m farewell_agent panduan` (buka buku panduan)
- **Mau cari pengetahuan?** — `py -m farewell_agent cari <topik>`
- **Error task?** — Cek `py -m farewell_agent sessions list` + `py -m farewell_agent sessions insights`
- **Mau ganti model tier?** — `py -m farewell_agent team divisi` (lebih kuat, lebih mahal)

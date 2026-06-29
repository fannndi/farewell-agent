# Basic Usage Examples

All examples assume you're in the `farewell-agent` directory:

```bash
cd C:\Users\You\Documents\farewell-agent
```

## Scenario 1: New Project, First Time

```bash
# 1. Setup dependencies (sekali aja)
py -m farewell_agent setup

# 2. Daily readiness
py -m farewell_agent daily

# 3. Register Flutter project
py -m farewell_agent setup-project C:\Users\You\Documents\my-flutter-app

# 4. Simpen catatan project
py -m farewell_agent memory save "Flutter 3.24, Riverpod, GoRouter"
py -m farewell_agent memory save --target user "Aku pemula, jelasin step by step"

# 5. Jalanin task pertama
py -m farewell_agent run "add a login screen with email and password"
```

Output yang bakal muncul:

```
[..] Intent: verification-loop
[OK] Config synced (build @ SPECIAL)
[..] Session: 001-my-flutter-app-1-143022

[?] Membuka buku panduan...
[Skills] Skill terkait (2)
  - [[dart-flutter-patterns]]: Source: `ecc/skills/dart-flutter-patterns/SKILL.md`
  - [[flutter-dart-code-review]]: Source: `ecc/skills/flutter-dart-code-review/SKILL.md`

[..] Exec: opencode run --agent build --model 9router/SPECIAL
[OK] Done (35s)

[Learning]:
[..] First 'verification-loop' task — note any project-specific workflow to MEMORY.md.
```

## Scenario 2: Natural Language Commands

### Audit project

```bash
py -m farewell_agent audit
```

Otomatis: switch ke plan mode → jalanin code-reviewer agent → security-check → report.

### Tambah fitur

```bash
py -m farewell_agent feature "payment gateway with midtrans"
```

Otomatis: plan → minta konfirmasi build mode → implement → review.

### Perbaiki error

```bash
py -m farewell_agent fix "login page not responding"
py -m farewell_agent run "perbaiki bug tanggal di laporan"
```

### Cek kesehatan system

```bash
py -m farewell_agent health
```

## Scenario 3: Using Knowledge Base

```bash
# Sebelum mulai, cek buku panduan
py -m farewell_agent panduan

# Cari skill yang relevan
py -m farewell_agent cari flutter riverpod
# Output:
#   Membuka buku panduan...
#   Mencari: flutter riverpod
#   [S] dart-flutter-patterns
#   [S] flutter-dart-code-review

# Kalau butuh knowledge spesifik
py -m farewell_agent cari docker deployment
py -m farewell_agent cari rust async pattern
```

## Scenario 4: Session Management

```bash
# Setelah beberapa kali run, cek riwayat
py -m farewell_agent sessions list
# Output:
#   [OK] fix login page not responding (45s) -- completed
#   [OK] add login screen with email and password (35s) -- completed
#   [FAIL] integrate payment gateway (120s) -- failed

# Lihat insight performa
py -m farewell_agent sessions insights
# Output:
#   3 tasks run (67% success) | weakest: feature (0/1)

# Cek budget
py -m farewell_agent cost status
# Output:
#   Today: $0.45 / $5.00
#   Month: $12.30 / $50.00
#   Recent Executions:
#   OK 001-my-flutter-app | feature | build | integrate payment gateway
#   OK 001-my-flutter-app | security | security-reviewer | audit auth
```

## Scenario 5: Multi-Project

```bash
# Register multiple projects
py -m farewell_agent setup-project C:\Users\You\Documents\service-hub
py -m farewell_agent setup-project C:\Users\You\Documents\web-app

# List all
py -m farewell_agent project
# Output:
#   001 - farewell-agent (python, PYTHON)
#   002 - service-hub (flutter, DART) <- active
#   003 - web-app (nextjs, TYPESCRIPT)

# Switch project
py -m farewell_agent project 003
py -m farewell_agent run "fix the nav bar responsiveness"
```

## Scenario 6: Obsidian Integration

**Setup:** tambah `OBSIDIAN_VAULT=` di `api-key.txt`, lalu:

```bash
# Ekstrak semua pengetahuan dari 5 repo ke vault
py -m farewell_agent extract-knowledge
# Output: ECC: 271 skills | awesome: 212 entries | 9Router | Hermes | Self-Evolution

# Di Obsidian, muncul folder _farewell-agent/ dengan isi:
#   _Index.md              ← mulai dari sini
#   awesome-opencode.md    ← 212 entries
#   9router.md             ← LLM Router docs + combos
#   hermes-agent.md        ← 205k stars agent
#   hermes-self-evolution.md ← optimization pipeline
#   ecc/                   ← 271 skills (organized by category)
```

Setiap `memory save` otomatis sinkron ke vault:

```bash
py -m farewell_agent memory save "Flutter 3.24, Riverpod 2.5"
# Otomatis nulis ke: vault/001-project/MEMORY.md
```

Setiap `run` otomatis nambah session note ke vault:

```bash
py -m farewell_agent run "fix date parsing"
# Otomatis nambah baris ke: vault/001-project/Session-Log.md
```

## Scenario 7: Research / Learn

```bash
# Mode riset
py -m farewell_agent learn "what is the best state management for Flutter?"
# Otomatis: plan mode → docs-lookup agent → research → hasil

# Belajar topik baru
py -m farewell_agent run "belajar docker compose postgresql"
# Otomatis: detek "belajar" → learn workflow → plan mode → research
```

## Copy-Paste Cheatsheet

```bash
# Setup
py -m farewell_agent setup
py -m farewell_agent daily

# Kerja
py -m farewell_agent run "fix bug"
py -m farewell_agent run "tambah fitur login"
py -m farewell_agent run "audit security"

# Knowledge
py -m farewell_agent cari flutter riverpod
py -m farewell_agent panduan

# Memory
py -m farewell_agent memory save "project notes"
py -m farewell_agent sessions list
py -m farewell_agent status
```

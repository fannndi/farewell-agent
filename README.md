# Farewell Agent

```
Kamu: "buat fitur login"
  │
  ▼
┌─────────────────────────────────────────┐
│  Baca Obsidian vault    Refine prompt   │
│  Pilih AI model         Eksekusi       │
│  Pastikan selalu ada FOOTER            │
│  Simpan ke Obsidian vault              │
└─────────────────────────────────────────┘
  │
  ▼
✅ Selesai. (45s)
---
### FOOTER
Project: 001-project | Session: repl-a1b2 | Next: test hasilnya
---
```

**Farewell Agent adalah AI layer pribadi.** Dia duduk antara kamu dan AI model.
Kamu ngomong natural — dia urus sisanya.

---

## Mulai

```bash
# Jalanin (REPL mode — tinggal ketik)
py -m farewell_agent

# Atau langsung
py -m farewell_agent repl
```

Contoh di REPL:
```
> buat program kalkulator sederhana
[OK] Done (30s)
---
> cek kesehatan 9router
[Daily] 9Router running
---
> evolusi
[Evolution] 8 siklus, level 5 tercapai
---
> keluar
Sampai jumpa!
```

---

## 4 Command

| Perintah | Fungsi |
|----------|--------|
| **`/daily`** | Start 9Router + npm update + pull 3 repo + health check |
| **`/setup-project C:\path`** | Daftarin project + extract guide book dari Obsidian + switch aktif |
| **`/start-project`** | Auto-detect direktori sekarang → daftarin + siap |
| **`/evolution`** | **Pull 5 repo + generate scenario + execute + level up/down** |

---

## Evolution — Auto-Loop

Ini inti Farewell Agent. Setiap `/evolution`:

```
┌─ 1. Pull 5 repo tools (ECC, 9Router, Hermes, dll)
├─ 2. Extract pengetahuan baru ke Obsidian
├─ 3. Analisis kelemahan diri:
│     • Model mana yg sering missing FOOTER?
│     • Task class mana yg success rate rendah?
│     • Area apa yg belum pernah dites?
├─ 4. Generate scenario sesuai kelemahan + level
├─ 5. Eksekusi pake model SPECIAL (gratis)
├─ 6. Verifikasi hasil:
│     ✅ PASS → naik level
│     ❌ FAIL → retry 1x
│     ❌ FAIL 2x → turun level
└─ 7. Loop → ulangi sampai budget harian habis
```

**Di hari libur:** tinggal jalanin `/evolution`, dia auto-loop sampai token abis.

```
Contoh binge evolution (8 siklus):
  Evo 1: Level 1 basic-io      ✅ PASS (12s)
  Evo 2: Level 2 function      ✅ PASS (25s)
  Evo 3: Level 3 multi-file    ❌ FAIL → retry → ✅ (45s)
  Evo 4: Level 4 external-lib  ✅ PASS (60s)
  Evo 5: Level 5 architecture  ✅ PASS (90s)
  Evo 6: Level 6 database      ❌ FAIL (2x) → turun ke 5
  Evo 7: Level 5 design        ✅ PASS (80s)
  Evo 8: Level 6 full-stack    ✅ PASS (3m)
  ── Budget limit reached. Lanjut besok! ──
```

---

## Org & Model

| Model | Role | Tools | Biaya |
|-------|------|-------|-------|
| `LEADER_1` | Orchestrator premium | read-only + delegasi | Mahal |
| `LEADER_2` | Orchestrator premium | read-only + delegasi | Mahal |
| `SPECIAL` | Orchestrator gratis | read-only + delegasi | **Gratis** |
| `WORKER` | Executor | write-only | Murah |
| Lainnya | Fallback `build` | full access | - |

Cuma model di `org_registry` yang dapet multi-agent.
Edit `.farewell/roles.json` buat daftarin model baru.

---

## Obsidian Vault — Sumber Pengetahuan

```
Obsidian Vault/
  _farewell-agent/
    projects/
      001-farewell-agent/
        MEMORY.md           ← Catatan project (max 2.200 char)
        USER.md             ← Profil user
        Session-Log.md      ← Riwayat session
        Chat-Log.md         ← Percakapan REPL (setiap chat tercatat)
        guide-*.md          ← Panduan per stack
```

**Setiap interaksi:**
1. Baca Obsidian vault buat konteks
2. Proses + kirim ke AI model
3. Tulis hasil ke `Chat-Log.md`
4. Update `MEMORY.md` kalau ada pelajaran baru

---

## FOOTER — Quality Gate

**Setiap output dari AI model WAJIB diakhiri FOOTER.**

```
---
### FOOTER
Project: 001-project | Session: repl-a1b2 | Next: test hasilnya
---

Tidak ada FOOTER = proses tidak selesai.
Kalau proses berhenti di tengah (crash / Ctrl+C), recovery otomatis.
```

---

## Auto-Tune

Setiap 10 task, Farewell Agent:
- Evaluasi mana model paling cocok per task class
- Update `task_model_preferences` di `roles.json`
- Catat ke MEMORY.md + sync Obsidian

Manual: `fa evolve` atau `fa analyze --suggest`

---

## Arsip Command (masih bisa dipake)

```
fa run "task"           → Jalanin task via OpenCode
fa status               → Status lengkap
fa org                  → Org chart
fa analyze --suggest    → Report performa model
fa memory show/save     → Kelola MEMORY.md
fa cari <topik>         → Cari di Obsidian vault
fa panduan              → Index buku panduan
fa setup                → Clone dependencies
fa project              → List / switch project
```

---

## Quick Start

```bash
# 1. Clone + setup
git clone https://github.com/fannndi/farewell-agent.git
cd farewell-agent
pip install -e .
py -m farewell_agent setup

# 2. Start 9Router + daily
py -m farewell_agent daily

# 3. Mulai REPL
py -m farewell_agent repl

# 4. Atau langsung
py -m farewell_agent
```

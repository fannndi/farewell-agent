# Farewell Agent

> Kamu ngomong. Dia kerja. **Obsidian nyatet.**

---

## Apa Ini?

Farewell Agent adalah **AI agent pribadi** yang duduk di antara kamu dan AI model.

```
Kamu: "buat fitur login page"
       │
       ▼
  ┌───────────────────────────────────┐
  │  1. Baca Obsidian vault          │
  │     (konteks project, MEMORY.md) │
  │  2. Refine prompt + pilih model  │
  │  3. Kirim ke AI model            │
  │  4. Pastikan selalu ada FOOTER   │
  │  5. Tulis ke Obsidian vault      │
  │     (Chat-Log.md)                │
  └───────────────────────────────────┘
       │
       ▼
Kamu: "buat fitur login page" ✅ (45s)
---
### FOOTER
Project: 001-project | Next: test hasilnya
---
```

**Tidak ada syntax. Tidak ada command yang harus dihafal. Cuma ngomong.**

---

## Cara Pakai

```bash
# Mulai REPL (tinggal ketik apapun)
py -m farewell_agent

# Atau pake shortcut
py -m farewell_agent repl
```

### Yang bisa kamu lakuin di REPL:

| Kamu bilang | Dia lakuin |
|-------------|-----------|
| `buat fitur login dengan flask` | Baca vault → refine → kirim ke AI → FOOTER → simpen ke Obsidian |
| `cek kesehatan` | Daily: start 9Router + npm update + health check |
| `update tools` | Evolution: pull 5 repo + extract + auto-apply |
| `daftarin project flutter di C:\project` | Setup: register + extract guide + switch |
| `/help` | Lihat bantuan |
| `exit` / `keluar` | Simpan session |

### Atau panggil langsung (tanpa REPL):

```bash
fa daily                          # rutinitas harian
fa evolution                      # update tools + extract
fa setup-project C:\flutter-app   # daftarin project
fa start-project                  # mulai project dari CWD
fa run "buat fitur login"         # panggil AI langsung
```

---

## Cara Kerja: Obsidian First

Setiap interaksi:

1. **Sebelum eksekusi** → baca Obsidian vault (konteks, MEMORY.md, skill terkait)
2. **Saat eksekusi** → AI model kerja dengan konteks kaya
3. **Setelah eksekusi** → tulis ke Obsidian vault:
   - `Chat-Log.md` — riwayat percakapan
   - `MEMORY.md` — pelajaran baru
   - `Session-Log.md` — ringkasan session

Vault location: `_farewell-agent/projects/{code}-{name}/`

---

## Org & Model

Cuma model di `org_registry` yang dapet multi-agent:

| Model | Role | Tools |
|-------|------|-------|
| `LEADER_1` | Orchestrator (premium) | read-only + delegasi |
| `SPECIAL` | Orchestrator (gratis) | read-only + delegasi |
| `WORKER` | Executor | write-only |

Model lain (Free_Chat, dll) → fallback ke `build` (single agent).

Edit `.farewell/roles.json` buat daftarin model baru.

---

## 4 Command Utama

```
┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────┐
│  DAILY   │ │SETUP-PROJ│ │START-PROJECT │ │  EVOLUTION   │
│ cek      │ │daftarin  │ │mulai project │ │update tools  │
│ kesehatan│ │+ extract │ │dari folder   │ │+ extract     │
│ + update │ │+ switch  │ │ini           │ │+ auto-apply  │
└──────────┘ └──────────┘ └──────────────┘ └──────────────┘
```

Semua otomatis: detect intent → execute → FOOTER → simpen ke Obsidian.

---

## Footer (WAJIB)

Setiap output diakhiri:

```
---
### FOOTER
Project: 001-project | Session: repl-a1b2c3
Next: cek hasilnya
---
```

**Tidak ada FOOTER = proses belum selesai.** Ada recovery otomatis.

---

## Obsidian Sync

```
Obsidian Vault/
  _farewell-agent/
    projects/
      001-farewell-agent/
        MEMORY.md           ← catatan project
        USER.md             ← profil user
        Session-Log.md      ← riwayat session
        Chat-Log.md         ← percakapan REPL
        guide-python.md     ← panduan dari vault
```

---

## Auto-Evolve

Setiap 10 task → Farewell Agent:
1. Evaluasi model mana paling cocok per task
2. Update preferensi otomatis
3. Catat ke MEMORY.md + sync Obsidian

Manual: `fa evolve` atau ketik `evolusi` di REPL.

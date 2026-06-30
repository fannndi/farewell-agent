# Farewell Agent

> Asisten pribadi yang ngomong sama AI buat kamu.

---

## Cara Kerja

Farewell Agent punya **2 mode**:

| Mode | Bisa apa? | Agent |
|------|-----------|-------|
| **plan** | Baca kode, riset, rencanain. **No write.** | Planner, Architect |
| **build** | Nulis kode, fix bug, deploy. **Full akses.** | Orchestrator -> Executor |

## Siapa Siapa

```
LEADER_1 / SPECIAL  ───→  Orchestrator (read-only, delegasi)
WORKER              ───→  Planner (read-only) / Executor (write-only)
Free_Chat / lain    ───→  Build fallback (single agent)
```

Cuma model yang terdaftar di **Org Registry** yang dapet multi-agent:
```
fa org
  Org Registry (4 models):
    LEADER_1  -> orchestrator
    LEADER_2  -> orchestrator
    SPECIAL   -> orchestrator
    WORKER    -> executor
```

---

## Cara Mulai

```bash
# 1. Install
pip install -e .

# 2. Setup dependencies
py -m farewell_agent setup

# 3. Cek kesehatan
py -m farewell_agent daily

# 4. Jalanin tugas pertama
py -m farewell_agent run "bikin file python hello world"
```

---

## Perintah

| Kamu bilang | Artinya |
|-------------|---------|
| `fa run "buat fitur"` | Jalanin task |
| `fa status` | Lihat status |
| `fa analyze --suggest` | Liat performa model |
| `fa org` | Liat org chart |
| `fa evolve` | Evolusi otomatis |
| `fa daily` | Cek kesehatan |
| `fa memory show` | Lihat catatan |
| `fa memory save "isi"` | Simpan catatan |

Tips: bikin alias `fa` di terminal.

---

## Setup Org (tambah model sendiri)

Edit `.farewell/roles.json`:

```json
{
  "schema_version": 3,
  "org_registry": ["LEADER_1", "LEADER_2", "SPECIAL", "WORKER", "MODEL_BARU"],
  "resolve": {
    "LEADER_1": { "role": "orchestrator", "agent": "team" },
    "MODEL_BARU": { "role": "executor", "agent": "senior-engineer" }
  }
}
```

Lalu tambah key-nya ke `api-key.txt`:
```
MODEL_BARU=oc/model-baru-xyz
```

Model yang **tidak** di `org_registry` otomatis pake `build` (single agent).

---

## Recovery (proses berhenti di tengah)

Kalau proses crash atau ke Ctrl+C di tengah jalan:
1. Farewell Agent deteksi lock file sisanya
2. Session yang kepotong ditandai "interrupted"
3. Lain kali jalanin task, recovery otomatis
4. Footer yang hilang artinya proses belum selesai

Manual: tinggal jalanin `fa run` lagi.

---

## Footer

Setiap jawaban AI selalu diakhiri dengan:

```
---
### FOOTER
Project: 001-farewell-agent | Session: a1b2c3
Next: coba jalankan perintah selanjutnya
```

**Tidak ada FOOTER = proses belum selesai.**

---

## Auto-Evolve

Setiap 10 tugas, Farewell Agent:
1. Cek footer rate (target 100%)
2. Evaluasi model mana paling cocok per task class
3. Update task_model_preferences otomatis
4. Catat pelajaran ke MEMORY.md + sync ke Obsidian

Jalanin manual: `fa evolve`

---

## Butuh Bantuan?

- `fa cari <topik>` — cari di buku panduan
- `fa --help` — semua perintah

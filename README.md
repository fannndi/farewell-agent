# Farewell Agent

> Asisten pribadi yang ngomong sama AI buat kamu.

---

## Cara Kerja

```
Farewell Agent duduk di antara kamu dan AI model.
Kamu bilang sesuatu -> dia rapiin + konteks + kirim ke AI -> selalu ada FOOTER.
```

**2 mode:**
| Mode | Agent | Tools |
|------|-------|-------|
| `plan` | Planner, Architect | Read-only — riset, rencana |
| `build` | Orchestrator -> Executor | Full — nulis, fix, deploy |

---

## 4 Command Utama

### `/daily` — Jalanin rutinitas harian

```
fa daily
```

1. Start 9Router (kalau belum jalan)
2. Git pull ECC + awesome-opencode + 9Router
3. `npm update` package 9Router
4. Render config + health check
5. Laporan ke console

### `/setup-project <path>` — Daftarin project baru

```
fa setup-project C:\project\flutter-app
```

1. Scan stack framework
2. Register project
3. Extract knowledge dari Obsidian vault -> bikin `guide-{stack}.md`
4. Inject `.farewell/` symlink
5. Switch active ke project baru -> **footer langsung aktif**

### `/start-project` — Mulai project (dari CWD)

```
cd C:\project\baru
fa start-project
```

1. Auto-detect framework
2. Register + extract guide + switch
3. "Project [X] siap. Footer aktif."

### `/evolution` — Update tools + extract + auto-apply

```
fa evolution
```

1. Git pull 5 repo: **ECC, awesome-opencode, 9Router, Hermes Agent, Hermes Self-Evolution**
2. Extract knowledge ke Obsidian vault
3. Auto-detect ECC skill baru -> update manifest
4. Render ulang config
5. Catat ke MEMORY.md + Obsidian

---

## Perintah Lain

| Kamu bilang | Artinya |
|-------------|---------|
| `fa run "buat fitur"` | Jalanin task ke AI |
| `fa status` | Lihat status |
| `fa org` | Lihat org chart |
| `fa analyze --suggest` | Report performa model |
| `fa evolve` | Evolusi pattern & model tuning |
| `fa memory show/save` | Kelola MEMORY.md |
| `fa panduan` | Index buku panduan |
| `fa cari <topik>` | Cari di Obsidian vault |

---

## Org & Model

Cuma model di `org_registry` yang dapet multi-agent:

```
LEADER_1 -> orchestrator (SPECIAL)
SPECIAL  -> orchestrator (SPECIAL)
WORKER   -> executor      (senior-engineer)
Lainnya  -> build (single agent, fallback)
```

Edit `.farewell/roles.json` buat daftarin model baru.

---

## Footer

```
---
### FOOTER
Project: 001-farewell-agent | Session: a1b2c3
Next: coba jalankan perintah selanjutnya
```

**Tidak ada FOOTER = proses belum selesai.** Ada recovery otomatis kalau proses berhenti di tengah.

---

## Auto-Evolve

Setiap 10 tugas:
1. Cek footer rate target 100%
2. Evaluasi model per task class -> update preferensi
3. Catat ke MEMORY.md + sync Obsidian

Manual: `fa evolve`

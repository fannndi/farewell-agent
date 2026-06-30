# Farewell Agent

> Kamu punya asisten pribadi yang bisa ngomong sama AI buat kamu.

---

## Cerita Singkat

Bayangin kamu punya **teman yang ngerti teknologi**. Kamu bilang "bikin sesuatu" — dia tahu maksud kamu, nanya detail yang kurang, ngobrol sama AI model yang tepat, lalu kasih kamu jawaban yang rapi + saran langkah selanjutnya.

**Itu Farewell Agent.**

Dia duduk di antara kamu dan AI model. Setiap kali kamu kasih tugas, dia:
1. **Ngerapiin** perintah kamu biar jelas
2. **Nambahin konteks** dari catatan project sebelumnya
3. **Kirim** ke AI model paling cocok
4. **Ngecek** jawaban AI — selalu ada FOOTER biar kamu tahu project apa, sesi apa, dan harus ngapain selanjutnya
5. **Belajar** dari setiap interaksi — makin sering dipake, makin pinter

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

## Perintah Sehari-hari

| Kamu bilang | Artinya |
|-------------|---------|
| `fa run "buat fitur login"` | Jalanin task ke AI |
| `fa daily` | Cek kesehatan + update |
| `fa project` | Lihat project terdaftar |
| `fa project 001` | Pindah project |
| `fa status` | Lihat status lengkap |
| `fa memory show` | Lihat catatan project |
| `fa memory save "isi catatan"` | Simpan catatan |
| `fa evolve` | Evolusi — biar makin pinter |

Tips: bikin alias `fa` di terminal.

---

## Footer

Setiap jawaban dari AI selalu diakhiri dengan:

```
---
### FOOTER
Project: 001-farewell-agent | Session: a1b2c3
Next: coba jalankan perintah selanjutnya
```

Ini penting biar kamu selalu tahu:
- **Project apa** yang lagi dikerjain
- **Sesi** yang sedang berlangsung
- **Langkah selanjutnya** yang bisa kamu ambil

---

## Auto-Evolve

Farewell Agent bisa belajar sendiri. Setiap 10 tugas, dia:
1. Cek apakah FOOTER selalu muncul
2. Evaluasi model mana yang paling cocok buat tugas tertentu
3. Catat pelajaran ke MEMORY.md

Jalanin manual kapan aja: `fa evolve`

---

## Butuh Bantuan?

- `fa cari <topik>` — cari di buku panduan (Obsidian vault)
- `fa panduan` — buka index buku panduan
- `fa --help` — semua perintah

---

Dibuat dengan ❤️ biar kamu nggak perlu jadi expert buat pake AI.

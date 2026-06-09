# SPK Pemilihan KOL Instagram — UMKM F&B Bali

Sistem Pendukung Keputusan berbasis web menggunakan metode Weighted Sum Model (WSM) untuk membantu UMKM sektor F&B di Bali memilih Key Opinion Leader (KOL) Instagram secara objektif.

---

## A. Cara Menjalankan di Komputer Lokal

### Persyaratan
- Python 3.10 atau lebih baru ([download di python.org](https://python.org))
- Browser modern (Chrome, Firefox, Edge)

### Langkah-langkah

**1. Extract folder & buka terminal di dalamnya**
```bash
cd spk_kol_mvp
```

**2. Install semua library (sekali saja, ~2 menit)**
```bash
pip install -r requirements.txt
```

**3. Jalankan sistem**
```bash
python main.py
```

**4. Buka browser**
```
http://localhost:8000
```

Sistem otomatis: (a) membuat database SQLite, (b) mengisi 52 KOL data F&B Bali, (c) menyiapkan 5 kriteria default. Tidak perlu setup tambahan.

---

## B. Cara Deploy Online (Gratis) — untuk Sesi Testing dengan Responden

### Opsi 1: Railway (Paling Mudah, Rekomendasi)

**1. Upload kode ke GitHub:**
- Buat akun GitHub (gratis) di github.com
- Buat repository baru, nama bebas (misal: `spk-kol-tesis`)
- Upload semua file di folder `spk_kol_mvp` ke repository tersebut

**2. Deploy ke Railway:**
- Daftar di [railway.app](https://railway.app) pakai akun GitHub
- Klik "New Project" → "Deploy from GitHub repo"
- Pilih repository yang baru dibuat
- Railway akan otomatis detect Python + menjalankan deploy

**3. Set environment variable:**
- Di Railway dashboard → tab Variables
- Tambahkan: `PORT=8000`
- Tambahkan volume di /data dan set `DB_PATH=/data/spk_kol.db` (agar data persisten)

**4. Aktifkan domain publik:**
- Tab Settings → Networking → Generate Domain
- URL muncul: `https://spk-kol-tesis-xxxx.up.railway.app`
- Bagikan URL ini ke responden UMKM via WhatsApp

**Free tier:** $5 kredit/bulan — cukup untuk seluruh proses testing.

### Opsi 2: Render

1. Daftar di [render.com](https://render.com)
2. New Web Service → Connect GitHub repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Tunggu deploy selesai, dapat URL publik

**Catatan Render:** Free tier akan "tidur" setelah 15 menit tanpa traffic — request pertama akan lambat. Cocok untuk testing terjadwal.

---

## C. Fitur Sistem (Memenuhi F01–F06 dari Tesis)

| Kode | Fitur | Lokasi |
|------|-------|--------|
| F01 | Database KOL (52 kandidat) | Halaman Dashboard & Cari KOL |
| F02 | Filter & Pencarian (niche + followers) | Halaman Cari KOL |
| F03 | Kalkulasi WSM otomatis | Backend, dipicu tombol Hitung Ranking |
| F04 | Tampilan Ranking + kontribusi per kriteria | Halaman Hasil Ranking |
| F05 | Penyesuaian Bobot via slider | Halaman Cari KOL |
| F06 | Detail Profil KOL | Klik tombol Detail di tabel ranking |

---

## D. Kriteria WSM (Bobot Default)

- **C1 Engagement Rate** — 35%
- **C2 Content Quality** — 20%
- **C3 Niche Relevance** — 20%
- **C4 Posting Consistency** — 15%
- **C5 Followers Count** — 10%

Bobot dapat disesuaikan pengguna melalui slider di halaman Cari KOL.

---

## E. Mengganti/Menambah Data KOL

Untuk update data KOL dengan hasil riset lapanganmu sendiri:

1. Edit file `seed_data.py` → bagian `KOL_DATA`
2. Tambah/hapus/edit entri sesuai kebutuhan
3. Hapus file `spk_kol.db` (database lama)
4. Jalankan ulang `python main.py` — database otomatis dibangun ulang dengan data baru

Format entri:
```python
{"username":"contoh_akun","nama_lengkap":"Nama","niche":"Food Review",
 "bio":"Bio singkat","followers":15000,"avg_likes":1200,"avg_comments":35,
 "engagement_rate":8.23,"posting_consistency":18,"content_quality_score":4.2,
 "niche_relevance":5,"instagram_url":"https://instagram.com/contoh_akun"},
```

---

## F. Struktur Direktori

```
spk_kol_mvp/
├── main.py              # Entry point — FastAPI app + 7 routes
├── database.py          # ORM models 5 tabel (SQLite via SQLAlchemy)
├── wsm.py               # Modul kalkulasi WSM + normalisasi min-max
├── seed_data.py         # 52 KOL + 5 kriteria untuk inisialisasi
├── requirements.txt     # Daftar library Python
├── Procfile             # Konfigurasi deploy Railway/Heroku
├── runtime.txt          # Versi Python (3.11.9)
├── templates/           # 6 file HTML (Jinja2)
│   ├── base.html
│   ├── dashboard.html
│   ├── search.html
│   ├── results.html
│   ├── detail.html
│   └── riwayat.html
└── static/
    └── style.css
```

---

## G. Troubleshooting

**Error: "ModuleNotFoundError"**
→ Library belum terinstall. Jalankan ulang: `pip install -r requirements.txt`

**Error: "Address already in use"**
→ Port 8000 dipakai aplikasi lain. Edit `main.py` baris terakhir, ganti `port=8000` jadi `port=8001`

**Halaman blank atau error 500**
→ Hapus file `spk_kol.db`, jalankan ulang `python main.py`

**Data hilang setelah restart di Railway**
→ Belum set persistent volume. Di Railway Variables, set `DB_PATH=/data/spk_kol.db` dan attach volume ke /data

---

## H. Lisensi & Penggunaan

Dikembangkan sebagai bagian dari penelitian tesis:

> **Weighted Sum Model dalam Sistem Pendukung Keputusan Berbasis Web untuk Pemilihan Key Opinion Leader pada UMKM Sektor F&B di Bali**
>
> Kadek Agus Yusida — NIM 2415795011
> Program Magister Terapan Manajemen Pemasaran Inovasi & Teknologi
> Politeknik Negeri Bali, 2026

Untuk keperluan riset akademis dan validasi penelitian.

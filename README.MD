# Sistem Rekomendasi Lowongan Kerja Bidang Penjualan dan Bisnis

Sistem rekomendasi lowongan kerja bidang penjualan dan bisnis berbasis **Large Language Model (LLM)** dan **Knowledge Graph**. Sistem menggunakan Llama 3.2 untuk membantu pengguna mengekstraksi kriteria pencarian dari bahasa alami, serta Knowledge Graph untuk merepresentasikan hubungan antara kriteria pengguna dan data lowongan kerja dalam proses pencocokan dan pemeringkatan rekomendasi.

## 1. Project Overview

Sistem ini dirancang untuk membantu pengguna menemukan lowongan kerja di bidang penjualan dan bisnis berdasarkan tujuh kriteria:

- Posisi
- Lokasi
- Pendidikan
- Pengalaman
- Tipe pekerjaan
- Gaji minimum
- Gender

LLM digunakan untuk membantu memahami input pengguna dalam bahasa alami dan mengekstraksi kriteria pencarian. Knowledge Graph digunakan untuk merepresentasikan relasi antara lowongan dan atributnya, sedangkan proses matching dan ranking dilakukan menggunakan mekanisme pencocokan berbasis kriteria.

## 2. Teknologi yang Digunakan

- **Python** — Bahasa pemrograman backend
- **FastAPI** — Backend dan REST API
- **Uvicorn** — ASGI server
- **Pandas** — Pengolahan dataset
- **NetworkX** — Representasi dan pengelolaan Knowledge Graph
- **Ollama** — Menjalankan model LLM secara lokal
- **Llama 3.2** — Ekstraksi kriteria dari bahasa alami
- **HTML, CSS, JavaScript** — Frontend

## 3. Persiapan Environment

Buka terminal pada folder utama project, kemudian jalankan perintah berikut untuk membuat virtual environment:

```powershell
python -m venv .venv
```

Aktifkan virtual environment:

```powershell
.venv\Scripts\activate
```

Jika berhasil, akan muncul `(.venv)` di awal terminal, misalnya:

```text
(.venv) PS C:\Users\...\project>
```

**Catatan:** Setelah membuat virtual environment, lakukan reload Visual Studio Code melalui `Ctrl + Shift + P`, kemudian cari dan pilih `Developer: Reload Window` jika diperlukan.

## 4. Instalasi Library

Pastikan virtual environment sudah aktif, kemudian instal seluruh library yang dibutuhkan:

```bash
python -m pip install "fastapi>=0.110" "uvicorn[standard]>=0.29" "pandas>=2.0" "networkx>=3.0" "requests>=2.31"
```

## 5. Instalasi Ollama dan Model AI

Unduh dan instal [Ollama](https://ollama.com/).

Setelah instalasi selesai, unduh model Llama 3.2:

```bash
ollama pull llama3.2
```

Periksa apakah model sudah berhasil terpasang:

```bash
ollama list
```

Jalankan model AI:

```bash
ollama run llama3.2
```

Pastikan Ollama berjalan agar fitur AI pada aplikasi dapat digunakan.

### Mengakhiri sesi Ollama

Untuk keluar dari sesi interaktif Llama 3.2:

- Ketik `/bye`, kemudian tekan `Enter`.
- Atau tekan `Ctrl + D` pada terminal yang mendukung perintah EOF.

**Catatan:** Perintah `/bye` digunakan untuk keluar dari sesi interaktif Ollama. Layanan Ollama mungkin tetap berjalan di latar belakang.

## 6. Menjalankan Backend

Buka terminal baru di Visual Studio Code, kemudian masuk ke folder `backend`:

```powershell
cd backend
```

Pastikan virtual environment sudah aktif. Jika belum, aktifkan dari folder utama project:

```powershell
.venv\Scripts\activate
```

Kemudian jalankan server FastAPI:

```bash
uvicorn main:app --reload --port 8000
```

Jika backend berhasil dijalankan, aplikasi akan memuat dataset processed dan membangun Knowledge Graph secara otomatis saat startup.

Contoh log startup:

```text
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Waiting for application startup.
INFO service: Dataset aktif: ...\data\processed\penjualan_bisnis_clean.csv
INFO service: Jumlah lowongan: 1245
INFO service: Knowledge Graph: {'nodes': 2779, 'edges': 9363, 'job': 1245, 'attribute': 1534}
```

Jumlah data dan statistik Knowledge Graph dapat berubah sesuai dataset terbaru yang tersedia.

## 7. Mengakses Aplikasi

Setelah server berhasil dijalankan, buka browser dan akses:

**Aplikasi utama:**

http://127.0.0.1:8000/

**Dokumentasi API (Swagger UI):**

http://127.0.0.1:8000/docs

**Dokumentasi API (ReDoc):**

http://127.0.0.1:8000/redoc

Swagger UI dapat digunakan untuk melihat endpoint API, struktur request dan response, serta mencoba request secara langsung.

## 8. API Endpoint

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/api/health` | Memeriksa status backend, dataset, Knowledge Graph, dan Ollama |
| GET | `/api/meta` | Mendapatkan metadata sistem dan dataset |
| GET | `/api/jobs` | Mendapatkan daftar lowongan beserta filter dan pagination |
| GET | `/api/jobs/{job_id}` | Mendapatkan detail lowongan berdasarkan ID |
| POST | `/api/chat` | Memproses input bahasa alami dan ekstraksi kriteria menggunakan LLM |
| POST | `/api/recommend` | Menghasilkan rekomendasi lowongan berdasarkan kriteria pengguna |
| POST | `/api/reload` | Memuat ulang dataset dan membangun ulang Knowledge Graph |

Endpoint `/api/reload` memerlukan token autentikasi melalui header `X-Reload-Token` dan konfigurasi `RELOAD_TOKEN` pada environment.

Informasi request, response, parameter, dan schema API dapat dilihat lebih lengkap melalui Swagger UI di `/docs`.

## 9. Dataset dan Data Pipeline

Sistem menggunakan dataset lowongan kerja yang diperoleh melalui proses scraping, kemudian diproses sebelum digunakan oleh backend.

### Dataset utama

| File | Fungsi |
|---|---|
| `backend/data/raw/lowongan_penjualan_bisnis_kitalulus.csv` | Dataset raw hasil scraping |
| `backend/data/processed/penjualan_bisnis_clean.csv` | Dataset yang telah melalui preprocessing dan digunakan oleh sistem |
| `backend/data/sample_lowongan.csv` | Dataset sample untuk keperluan pengujian |

Dataset aktif aplikasi adalah `penjualan_bisnis_clean.csv` yang berada di direktori `backend/data/processed/`.

### Alur data

```text
KitaLulus
    |
    v
scraper.py
    |
    v
Raw Dataset (CSV)
    |
    v
pipeline.py
    |
    v
preprocessing.py
    |
    v
Processed Dataset (CSV)
    |
    v
JobService
    |
    v
Knowledge Graph
    |
    v
Matching & Ranking
    |
    v
Job Recommendation
```

## 10. Menjalankan Scraper Secara Manual

Scraper digunakan untuk mengambil data lowongan kerja dari KitaLulus berdasarkan kategori dan kata kunci yang telah ditentukan dalam program.

Pastikan virtual environment aktif dan terminal berada di folder utama project. Kemudian masuk ke direktori backend:

```powershell
cd backend
```

Jalankan scraper:

```bash
python scraper.py
```

Scraper akan mengambil data lowongan, melakukan transformasi awal terhadap data hasil scraping, dan menyimpan dataset raw pada lokasi yang telah ditentukan oleh konfigurasi sistem.

Dataset raw yang digunakan secara default:

```text
backend/data/raw/lowongan_penjualan_bisnis_kitalulus.csv
```

**Catatan:** Scraping memerlukan koneksi internet. Proses scraping dapat membutuhkan waktu bergantung pada jumlah data yang diambil dan kondisi koneksi.

## 11. Menjalankan Preprocessing Pipeline Secara Manual

Setelah proses scraping berhasil, preprocessing pipeline dapat dijalankan untuk membersihkan dan mempersiapkan dataset agar dapat digunakan oleh sistem rekomendasi.

Pastikan terminal berada di direktori `backend`:

```powershell
cd backend
```

Kemudian jalankan:

```bash
python pipeline.py
```

Pipeline akan membaca dataset raw, melakukan cleaning dan normalisasi data, memvalidasi dataset, kemudian menyimpan hasil preprocessing ke dataset processed.

Dataset processed yang digunakan oleh sistem secara default:

```text
backend/data/processed/penjualan_bisnis_clean.csv
```

Pipeline dirancang agar dataset processed sebelumnya tetap dipertahankan apabila proses preprocessing gagal.

### Urutan update dataset manual

```bash
python scraper.py
python pipeline.py
```

Setelah kedua proses berhasil, dataset processed sudah diperbarui. Agar backend yang sedang berjalan menggunakan dataset terbaru, lakukan reload dataset melalui endpoint `/api/reload` dengan token yang valid, atau restart backend.

## 12. Metode Sistem Rekomendasi

Sistem rekomendasi menggunakan Knowledge Graph untuk merepresentasikan lowongan kerja dan atribut yang berkaitan dengan lowongan tersebut.

Kriteria pengguna dicocokkan dengan atribut lowongan berdasarkan tujuh kriteria utama:

1. Posisi
2. Lokasi
3. Pendidikan
4. Pengalaman
5. Tipe pekerjaan
6. Gaji minimum
7. Gender

Setiap kriteria menghasilkan nilai pencocokan biner:

- `1` apabila kriteria lowongan sesuai dengan kriteria pengguna.
- `0` apabila kriteria lowongan tidak sesuai.

Nilai pencocokan dari setiap kriteria dijumlahkan untuk memperoleh skor total lowongan.

### Perhitungan skor matching

\[
S(j)=\sum_{i=1}^{7}M_i(u,j)
\]

Keterangan:

- \(S(j)\) = skor matching lowongan \(j\)
- \(M_i(u,j)\) = nilai pencocokan kriteria ke-\(i\) antara pengguna \(u\) dan lowongan \(j\)
- Nilai pencocokan setiap kriteria adalah `0` atau `1`

### Perhitungan persentase matching

\[
P(j)=\frac{S(j)}{7}\times100\%
\]

Persentase matching digunakan untuk menampilkan tingkat kesesuaian lowongan terhadap kriteria pengguna. Lowongan kemudian diurutkan berdasarkan skor matching untuk menghasilkan daftar rekomendasi.

## 13. Automatic Dataset Update

Project menyediakan script `daily_update.ps1` untuk mendukung proses pembaruan dataset secara otomatis.

Script ini mengintegrasikan proses scraping, preprocessing, dan reload dataset pada backend.

Secara umum, alur pembaruan meliputi:

1. Membuat backup dataset processed yang sedang digunakan.
2. Menjalankan scraper untuk memperoleh data terbaru.
3. Menjalankan preprocessing pipeline.
4. Memuat ulang dataset dan Knowledge Graph pada backend melalui endpoint reload.
5. Mempertahankan atau memulihkan dataset backup apabila proses update gagal.

Script ini dapat digunakan untuk menjalankan pembaruan dataset secara terjadwal melalui Windows Task Scheduler.

## 14. Menghentikan Backend

Untuk menghentikan server FastAPI, tekan:

```text
CTRL + C
```

pada terminal tempat backend sedang berjalan.

## 15. Troubleshooting

### Backend tidak dapat dijalankan

Pastikan:

- Terminal berada di direktori `backend`.
- Virtual environment telah aktif.
- Library yang dibutuhkan sudah terinstal.
- Port `8000` tidak sedang digunakan oleh proses lain.

### Fitur AI tidak berfungsi

Pastikan Ollama sudah terinstal, layanan Ollama berjalan, dan model Llama 3.2 tersedia.

Periksa model:

```bash
ollama list
```

Jika belum tersedia:

```bash
ollama pull llama3.2
```

### Dataset tidak ditemukan

Pastikan dataset processed tersedia pada lokasi:

```text
backend/data/processed/penjualan_bisnis_clean.csv
```

Jika dataset belum tersedia atau ingin memperbarui dataset, jalankan proses scraping dan preprocessing pipeline sesuai panduan di atas.

### Dataset terbaru belum tampil pada aplikasi

Setelah proses preprocessing selesai, backend perlu memuat ulang dataset agar data terbaru digunakan. Restart backend atau gunakan endpoint `/api/reload` dengan token yang valid.

---

## Catatan Tambahan

- Jalankan backend dari folder `backend` agar Python dapat menemukan `main.py` dan konfigurasi project dengan benar.
- Pastikan Ollama dan model Llama 3.2 tersedia ketika menggunakan fitur AI.
- Virtual environment harus diaktifkan sebelum menjalankan backend.
- Dataset raw dan processed memiliki fungsi yang berbeda. Backend menggunakan dataset processed sebagai sumber data utama.
- Jumlah data lowongan dan statistik Knowledge Graph dapat berubah setiap kali dataset diperbarui.
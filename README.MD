# Sistem Rekomendasi Lowongan Kerja

Sistem rekomendasi lowongan kerja berbasis **Large Language Model (LLM)** dan **Knowledge Graph** untuk bidang penjualan dan bisnis.

## 1. Persiapan Environment

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

**Catatan:** Setelah membuat virtual environment, lakukan reload Visual Studio Code melalui `Ctrl + Shift + P`, kemudian cari dan pilih **Developer: Reload Window** jika diperlukan.

## 2. Instalasi Library

Pastikan virtual environment sudah aktif, kemudian instal seluruh library yang dibutuhkan:

```bash
python -m pip install "fastapi>=0.110" "uvicorn[standard]>=0.29" "pandas>=2.0" "networkx>=3.0" "requests>=2.31"
```

## 3. Instalasi Ollama dan Model AI

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

**Mengakhiri sesi Ollama:**

Untuk keluar dari sesi interaktif Llama 3.2, gunakan salah satu cara berikut:

- Ketik `/bye`, kemudian tekan `Enter`.
- Tekan `Ctrl + D` pada terminal yang mendukung perintah EOF.

**Catatan:** Perintah `/bye` digunakan untuk keluar dari sesi interaktif Ollama. Layanan Ollama mungkin tetap berjalan di latar belakang.

## 4. Menjalankan Backend

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

Jika berhasil, terminal akan menampilkan informasi seperti berikut:

```text
INFO: Will watch for changes in these directories: [...]
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO: Started reloader process [...] using WatchFiles
INFO: Started server process [...]
INFO: Waiting for application startup.
INFO preprocessing: CSV dibaca: ...\data\lowongan_penjualan_bisnis.csv (1341 baris)
INFO preprocessing: Pra-pemrosesan selesai: 1341 lowongan, 30 atribut
INFO service: Knowledge Graph: {'nodes': 2852, 'edges': 8693, 'job': 1339, 'attribute': 1513}
INFO: Application startup complete.
```

## 5. Mengakses Aplikasi

Setelah server berhasil dijalankan, buka browser dan akses:

**Aplikasi:** http://127.0.0.1:8000/

## 6. Menghentikan Backend

Untuk menghentikan server FastAPI, tekan:

```text
CTRL + C
```

pada terminal tempat backend sedang berjalan.

---

**Catatan:**
- Jalankan backend dari folder `backend` agar Python dapat menemukan `main.py` dan konfigurasi project dengan benar.
- Pastikan Ollama dan model Llama 3.2 tersedia ketika menggunakan fitur AI.
- Virtual environment harus diaktifkan sebelum menjalankan backend.
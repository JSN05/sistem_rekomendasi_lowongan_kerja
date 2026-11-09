"""Konfigurasi backend. Semua nilai bisa diubah lewat environment variable."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# CSV hasil scraping Kita Lulus (letakkan di backend/data/ atau set CSV_PATH)
CSV_PATH = Path(os.getenv("CSV_PATH", DATA_DIR / "lowongan_penjualan_bisnis.csv"))
# Data contoh kecil, dipakai hanya jika CSV asli tidak ditemukan
SAMPLE_CSV_PATH = DATA_DIR / "sample_lowongan.csv"

# Folder frontend yang akan disajikan oleh backend (http://localhost:8000/beranda.html)
FRONTEND_DIR = Path(os.getenv("FRONTEND_DIR", BASE_DIR.parent / "frontend"))

# Ollama + Llama 3.2
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "60"))
USE_LLM = os.getenv("USE_LLM", "1") != "0"   # USE_LLM=0 -> paksa ekstraksi berbasis aturan

# Aturan gaji: "min" = salary_min lowongan >= gaji minimum pengguna (sesuai paper)
#              "max" = salary_max lowongan >= gaji minimum pengguna (lebih longgar)
SALARY_BASIS = os.getenv("SALARY_BASIS", "min")

KITALULUS_JOB_URL = "https://www.kitalulus.com/lowongan/detail/{slug}"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]

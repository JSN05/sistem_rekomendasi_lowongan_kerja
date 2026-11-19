"""Konfigurasi backend aplikasi rekomendasi lowongan kerja."""

import os
from pathlib import Path

# Direktori
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Dataset
RAW_CSV_PATH = Path(
    os.getenv(
        "RAW_CSV_PATH",
        str(RAW_DATA_DIR / "lowongan_penjualan_bisnis_kitalulus.csv")
    )
)

PROCESSED_CSV_PATH = Path(
    os.getenv(
        "PROCESSED_CSV_PATH",
        str(PROCESSED_DATA_DIR / "penjualan_bisnis_clean.csv")
    )
)

SAMPLE_CSV_PATH = DATA_DIR / "sample_lowongan.csv"

CSV_PATH = Path(
    os.getenv(
        "CSV_PATH",
        str(DATA_DIR / "lowongan_penjualan_bisnis.csv")
    )
)

# Frontend
FRONTEND_DIR = Path(
    os.getenv("FRONTEND_DIR", str(BASE_DIR.parent / "frontend"))
)

# Ollama (LLM)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "60"))

USE_LLM = os.getenv("USE_LLM", "1") != "0"

# Knowledge Graph
SALARY_BASIS = os.getenv("SALARY_BASIS", "min")

# Kitalulus
KITALULUS_JOB_URL = (
    "https://www.kitalulus.com/lowongan/detail/{slug}"
)

# Cors
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
]

# Reload
RELOAD_TOKEN = os.getenv("RELOAD_TOKEN", "")
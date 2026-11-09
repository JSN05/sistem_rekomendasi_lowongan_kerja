"""Pra-pemrosesan data lowongan (Bab 2.3 paper): data cleaning, normalization, case folding."""
import logging
import re
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("preprocessing")

# Kolom teks yang nilai aslinya disimpan (suffix _raw) untuk ditampilkan di UI,
# sedangkan versi yang sudah dinormalisasi dipakai untuk pencocokan.
DISPLAY_COLUMNS = [
    "job_title", "job_role", "company_name", "location_province", "location_city",
    "education_level", "job_type", "gender",
]
NUMERIC_COLUMNS = ["salary_min", "salary_max", "experience", "max_age"]


def _collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _normalize_education(v):
    if not isinstance(v, str):
        return v
    s = v.lower()
    s = re.sub(r"\b(minimal|min)\b\.?", " ", s)   # hapus kata "minimal"/"min"
    s = s.replace("/", " ")                        # "sma/smk" -> "sma smk"
    return _collapse(s)


def _normalize_hyphen(v):
    if not isinstance(v, str):
        return v
    return _collapse(v.lower().replace("-", " "))  # "full-time" -> "full time"


def _to_bool(v) -> bool:
    return str(v).strip().lower() in {"true", "1", "yes"}


def load_and_clean(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    log.info("CSV dibaca: %s (%d baris)", csv_path, len(df))

    # --- Data cleaning -------------------------------------------------
    df = df.drop_duplicates(subset="job_id").reset_index(drop=True)

    if "min_age" in df.columns and df["min_age"].isna().all():
        df = df.drop(columns="min_age")          # seluruh nilainya kosong

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # gaji 0 (min & max sekaligus) = gaji tidak dicantumkan -> missing value
    both_zero = df["salary_min"].fillna(0).eq(0) & df["salary_max"].fillna(0).eq(0)
    df.loc[both_zero, ["salary_min", "salary_max"]] = np.nan
    df.loc[df["max_age"].eq(0), "max_age"] = np.nan

    invalid = (df["salary_min"] > df["salary_max"]) | (df["salary_min"] < 0) | (df["salary_max"] < 0)
    if invalid.any():
        log.warning("%d lowongan memiliki gaji tidak valid", int(invalid.sum()))

    # indikator ketersediaan data
    df["salary_is_missing"] = df["salary_min"].isna() & df["salary_max"].isna()
    df["experience_is_missing"] = df["experience"].isna()
    df["max_age_is_missing"] = df["max_age"].isna()
    df["experience"] = df["experience"].fillna(0)  # kosong = tidak ada batas pengalaman

    for col in ("is_highlighted", "is_closed"):
        df[col] = df[col].map(_to_bool) if col in df.columns else False

    # --- Simpan nilai asli untuk tampilan -------------------------------
    for col in DISPLAY_COLUMNS:
        if col in df.columns:
            df[col + "_raw"] = df[col]

    # --- Case folding (semua kolom teks kecuali slug) --------------------
    for col in list(df.columns):
        if col == "slug" or col.endswith("_raw"):
            continue
        if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].map(lambda v: v.lower().strip() if isinstance(v, str) else v)

    # --- Data normalization ----------------------------------------------
    df["education_level"] = df["education_level"].map(_normalize_education)
    df["job_type"] = df["job_type"].map(_normalize_hyphen)
    df["gender"] = df["gender"].map(_normalize_hyphen)

    for col in NUMERIC_COLUMNS:
        df[col] = df[col].round().astype("Int64")

    log.info("Pra-pemrosesan selesai: %d lowongan, %d atribut", len(df), df.shape[1])
    return df


def _py(v):
    """Ubah nilai pandas (NA, numpy) menjadi tipe Python biasa agar bisa di-JSON-kan."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(v, "item"):
        return v.item()
    return v


def to_records(df: pd.DataFrame) -> list[dict]:
    return [{k: _py(v) for k, v in row.items()} for row in df.to_dict("records")]

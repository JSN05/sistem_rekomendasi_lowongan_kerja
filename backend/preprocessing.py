"""Pra-pemrosesan dataset lowongan kerja.
Mengikuti tahapan CLEANING 1-7 pada notebook Analisa Dataset.
"""

import logging
import re
import numpy as np
import pandas as pd
from pathlib import Path

log = logging.getLogger("preprocessing")

DISPLAY_COLUMNS = [
    "job_title",
    "job_role",
    "company_name",
    "location_province",
    "location_city",
    "education_level",
    "job_type",
    "gender",
]

NUMERIC_COLUMNS = [
    "salary_min",
    "salary_max",
    "experience",
    "max_age",
]


def clean_education_text(text):
    """Cleaning teks education_level sesuai CLEANING 5 notebook."""
    if pd.isna(text):
        return text

    text = str(text)
    text = re.sub(
        r"\b(minimal|min)\b",
        "",
        text,
        flags=re.IGNORECASE
    )
    text = text.replace("/", " ")

    return " ".join(text.split())


def _to_bool(value):
    """Memastikan nilai boolean dapat dibaca dengan benar."""
    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {
        "true", "1", "yes"
    }


def load_and_clean(csv_path: Path) -> pd.DataFrame:
    """Menjalankan preprocessing sesuai notebook analisis dataset."""

    # Membaca dataset dan mempertahankan job_id sebagai string.
    df_clean = pd.read_csv(
        csv_path,
        dtype={"job_id": "string"}
    )

    log.info(
        "CSV dibaca: %s (%d baris)",
        csv_path,
        len(df_clean)
    )

    # ==================================================
    # CLEANING 1
    # Pengecekan Duplikat & Penghapusan Kolom Kosong
    # ==================================================

    log.info("CLEANING 1: Menghapus duplikat dan min_age.")

    initial_rows = len(df_clean)

    df_clean.drop_duplicates(
        subset=["job_id"],
        inplace=True
    )

    removed_duplicates = initial_rows - len(df_clean)

    log.info(
        "Duplikat terhapus: %d baris",
        removed_duplicates
    )

    if "min_age" in df_clean.columns:
        df_clean.drop(
            columns=["min_age"],
            inplace=True
        )

    # ==================================================
    # Menyimpan teks asli untuk kebutuhan tampilan aplikasi
    # ==================================================

    for col in DISPLAY_COLUMNS:
        if col in df_clean.columns:
            df_clean[col + "_raw"] = df_clean[col]

    # ==================================================
    # CLEANING 2
    # Menangani Nilai Tidak Valid pada Gaji & Usia
    # ==================================================

    log.info("CLEANING 2: Menangani nilai gaji dan usia.")

    df_clean.loc[
        (df_clean["salary_min"] == 0)
        & (df_clean["salary_max"] == 0),
        ["salary_min", "salary_max"]
    ] = np.nan

    df_clean["max_age"] = df_clean["max_age"].replace(
        0,
        np.nan
    )

    invalid_salary = (
        (df_clean["salary_min"] > df_clean["salary_max"])
        | (df_clean["salary_min"] < 0)
        | (df_clean["salary_max"] < 0)
    )

    if invalid_salary.any():
        log.warning(
            "%d lowongan memiliki nilai gaji tidak valid.",
            int(invalid_salary.sum())
        )

    # ==================================================
    # CLEANING 3
    # Normalisasi Teks & Standardisasi Kategori
    # ==================================================

    log.info("CLEANING 3: Normalisasi kategori.")

    for col in ["education_level", "job_type", "gender"]:
        df_clean[col] = (
            df_clean[col]
            .str.strip()
            .str.lower()
        )

    # ==================================================
    # CLEANING 4
    # Penanganan Missing Values & Feature Flagging
    # ==================================================

    log.info("CLEANING 4: Membuat missing value flags.")

    df_clean["salary_is_missing"] = (
        df_clean[["salary_min", "salary_max"]]
        .isnull()
        .any(axis=1)
        .astype(int)
    )

    df_clean["experience_is_missing"] = (
        df_clean["experience"]
        .isnull()
        .astype(int)
    )

    df_clean["max_age_is_missing"] = (
        df_clean["max_age"]
        .isnull()
        .astype(int)
    )

    # Experience kosong diubah menjadi 0.
    # Salary dan max_age tetap NaN.
    df_clean["experience"] = (
        df_clean["experience"].fillna(0)
    )

    # ==================================================
    # CLEANING 5
    # Pembersihan Teks Khusus
    # ==================================================

    log.info("CLEANING 5: Pembersihan teks khusus.")

    df_clean["education_level"] = (
        df_clean["education_level"]
        .apply(clean_education_text)
    )

    df_clean["job_type"] = (
        df_clean["job_type"]
        .str.replace("-", " ", regex=False)
    )

    df_clean["gender"] = (
        df_clean["gender"]
        .str.replace("-", " ", regex=False)
    )

    # ==================================================
    # CLEANING 6
    # Standardisasi Tipe Data Numerik
    # ==================================================

    log.info("CLEANING 6: Konversi tipe data numerik.")

    for col in NUMERIC_COLUMNS:
        if col in df_clean.columns:
            df_clean[col] = (
                pd.to_numeric(
                    df_clean[col],
                    errors="coerce"
                )
                .round()
                .astype("Int64")
            )

    # ==================================================
    # CLEANING 7
    # Case Folding Global & Validasi Akhir
    # ==================================================

    log.info("CLEANING 7: Case folding.")

    object_cols = df_clean.select_dtypes(
        include=["object"]
    ).columns

    for col in object_cols:
        # job_id dan slug tidak diubah.
        # job_id dipertahankan karena merupakan identifier.
        if col not in ["job_id", "slug"]:
            df_clean[col] = df_clean[col].str.lower()

    # ==================================================
    # VALIDASI AKHIR DATASET
    # ==================================================

    log.info("Menjalankan validasi akhir dataset.")

    if df_clean.empty:
        raise ValueError(
            "Dataset kosong setelah preprocessing."
        )

    if df_clean["job_id"].isna().any():
        raise ValueError(
            "Terdapat job_id kosong."
        )

    if df_clean["job_id"].duplicated().any():
        raise ValueError(
            "Terdapat job_id duplikat setelah preprocessing."
        )

    log.info(
        "Ukuran dataset akhir: %s",
        df_clean.shape
    )

    log.info(
        "Jumlah duplikat job_id: %d",
        df_clean["job_id"].duplicated().sum()
    )

    log.info(
        "Pra-pemrosesan selesai: %d lowongan, %d atribut",
        len(df_clean),
        df_clean.shape[1]
    )

    return df_clean


def _py(value):
    """Mengubah nilai pandas/numpy menjadi tipe Python biasa."""

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "item"):
        return value.item()

    return value


def to_records(df: pd.DataFrame) -> list[dict]:
    """Mengubah DataFrame menjadi list dictionary."""

    return [
        {
            key: _py(value)
            for key, value in row.items()
        }
        for row in df.to_dict("records")
    ]
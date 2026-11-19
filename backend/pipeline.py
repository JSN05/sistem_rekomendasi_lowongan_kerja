
"""Pipeline preprocessing dataset lowongan kerja."""

import logging
import pandas as pd
import config
from preprocessing import load_and_clean
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

log = logging.getLogger("pipeline")

def validate_dataset(df):
    """Memvalidasi hasil preprocessing sebelum disimpan."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Hasil preprocessing bukan DataFrame.")

    if df.empty:
        raise ValueError("Dataset hasil preprocessing kosong.")

    required_columns = [
        "job_id",
        "job_title",
        "company_name"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Kolom wajib tidak ditemukan: {missing_columns}"
        )

    if df["job_id"].isna().any():
        raise ValueError("Masih terdapat job_id kosong.")

    if df["job_id"].duplicated().any():
        raise ValueError("Masih terdapat job_id duplikat.")

    log.info("Validasi dataset berhasil.")
    log.info("Jumlah baris: %s", len(df))
    log.info("Jumlah kolom: %s", len(df.columns))

def save_processed_dataset(df, output_file):
    """Menyimpan dataset dengan mekanisme penggantian atomik."""

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    temp_file = output_file.with_name(
        output_file.stem + ".tmp" + output_file.suffix
    )

    try:
        df.to_csv(
            temp_file,
            index=False,
            encoding="utf-8-sig"
        )

        check_df = pd.read_csv(temp_file)

        if len(check_df) != len(df):
            raise ValueError(
                "Jumlah baris CSV hasil penyimpanan tidak sesuai."
            )

        temp_file.replace(output_file)

    finally:
        if temp_file.exists():
            temp_file.unlink()

    log.info("Dataset processed berhasil disimpan: %s", output_file)


def run_pipeline():
    """Menjalankan keseluruhan proses preprocessing."""

    raw_file = config.RAW_CSV_PATH
    processed_file = config.PROCESSED_CSV_PATH

    log.info("Memulai pipeline preprocessing.")
    log.info("Dataset raw: %s", raw_file)

    if not raw_file.exists():
        raise FileNotFoundError(
            f"Dataset raw tidak ditemukan: {raw_file}"
        )

    df = load_and_clean(raw_file)

    validate_dataset(df)

    save_processed_dataset(df, processed_file)

    log.info("PIPELINE PREPROCESSING BERHASIL!")
    log.info("Total data: %s", len(df))

    return df

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception:
        log.exception(
            "Pipeline gagal. Dataset processed sebelumnya "
            "tetap dipertahankan."
        )
        raise
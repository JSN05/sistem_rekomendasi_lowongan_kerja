"""Scraping lowongan kerja Penjualan & Bisnis dari KitaLulus."""

import logging
import time
import pandas as pd
import requests
import config
from pathlib import Path

# Konfigurasi scraping
URL = "https://gql.kitalulus.com/graphql"
MAX_DATA = 2000
LIMIT_PER_PAGE = 30
OUTPUT_FILE = config.RAW_CSV_PATH

KEYWORDS_PENJUALAN_BISNIS = [
    "sales", "business development", "account executive", "account manager",
    "key account", "marketing", "digital marketing", "brand", "promotion",
    "promotor", "promoter", "customer relationship", "relationship officer",
    "partnership", "merchant", "commercial", "retail", "store", "outlet",
    "showroom", "e-commerce", "ecommerce", "marketplace", "trade marketing",
    "merchandising", "merchandiser", "telemarketing", "telesales"
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

log = logging.getLogger("scraper")


# Query GraphQL
QUERY = """
fragment VacancyCardFragment on Vacancy {
  id
  slug
  code
  positionName
  isHighlighted
  isClosed
  educationLevelStr
  salaryLowerBound
  salaryUpperBound
  updatedAtStr
  genderStr
  maxAge
  minExperience
  typeStr
  company {
    name
    code
    logoUrl
  }
  province {
    name
  }
  city {
    name
  }
  jobRole {
    displayName
  }
}

query Vacancies(
  $keyword: String,
  $tag: String,
  $pagination: CommonFilter,
  $filters: [SearchCategoryFilter!],
  $locations: [LocationAreaInput!],
  $haveMisiSeruLimit: Boolean,
  $userMaxEducation: String,
  $userJobSpecializationRoleIds: [ID!]
) {
  vacanciesV4(
    keyword: $keyword
    tag: $tag
    pagination: $pagination
    filters: $filters
    locations: $locations
    haveMisiSeruLimit: $haveMisiSeruLimit
    userMaxEducation: $userMaxEducation
    userJobSpecializationRoleIds: $userJobSpecializationRoleIds
  ) {
    hasNextPage
    list {
      ...VacancyCardFragment
    }
  }
}
"""


FILTERS = [
    {"key": "sortBy", "value": ["isHighlighted"]},
    {"key": "jobSpecializations", "value": []},
    {"key": "companyIndustries", "value": []},
    {"key": "educationLevels", "value": []},
    {"key": "gender", "value": []},
    {"key": "salary", "value": []},
    {"key": "types", "value": []},
    {"key": "jobLevels", "value": []},
    {"key": "locationSites", "value": []},
    {"key": "workExperience", "value": []},
]


def fetch_page(session, page):
    """Mengambil satu halaman data dari GraphQL."""

    variables = {
        "keyword": "",
        "tag": "",
        "locations": [],
        "haveMisiSeruLimit": True,
        "userMaxEducation": "",
        "userJobSpecializationRoleIds": [],
        "pagination": {
            "page": page,
            "limit": LIMIT_PER_PAGE
        },
        "filters": FILTERS
    }

    payload = {
        "operationName": "Vacancies",
        "variables": variables,
        "query": QUERY
    }

    try:
        response = session.post(URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError) as error:
        raise RuntimeError(
            f"Gagal mengambil data halaman {page}: {error}"
        ) from error

    if not isinstance(result, dict):
        raise RuntimeError(
            f"Respons halaman {page} tidak berbentuk JSON object."
        )

    if result.get("errors"):
        raise RuntimeError(
            f"GraphQL Error pada halaman {page}: {result['errors']}"
        )

    vacancies = result.get("data", {}).get("vacanciesV4")

    if not isinstance(vacancies, dict):
        raise RuntimeError(
            f"Struktur respons halaman {page} tidak sesuai."
        )

    jobs = vacancies.get("list")

    if not isinstance(jobs, list):
        raise RuntimeError(
            f"Data lowongan halaman {page} tidak valid."
        )

    has_next_page = vacancies.get("hasNextPage")

    if not isinstance(has_next_page, bool):
        raise RuntimeError(
            f"Informasi pagination halaman {page} tidak valid."
        )

    return jobs, has_next_page


def scrape_jobs():
    """Mengambil seluruh lowongan yang sesuai dengan keyword."""

    all_jobs = []
    page = 1

    log.info("Memulai scraping lowongan Penjualan & Bisnis KitaLulus.")

    with requests.Session() as session:
        while len(all_jobs) < MAX_DATA:

            jobs, has_next_page = fetch_page(session, page)

            if not jobs:
                log.info("Tidak ada data pada halaman %s.", page)
                break

            matched_count = 0

            for job in jobs:
                title = (job.get("positionName") or "").lower()

                if any(
                    keyword in title
                    for keyword in KEYWORDS_PENJUALAN_BISNIS
                ):
                    all_jobs.append(job)
                    matched_count += 1

                    if len(all_jobs) >= MAX_DATA:
                        break

            log.info(
                "Halaman %s | Data diambil: %s | "
                "Cocok filter: %s | Total terkumpul: %s",
                page,
                len(jobs),
                matched_count,
                len(all_jobs)
            )

            if len(all_jobs) >= MAX_DATA:
                log.info("Batas maksimum %s data tercapai.", MAX_DATA)
                break

            if not has_next_page:
                log.info("Sudah mencapai halaman terakhir.")
                break

            page += 1
            time.sleep(1)

    if not all_jobs:
        raise RuntimeError(
            "Tidak ada lowongan yang berhasil dikumpulkan. "
            "Dataset lama tidak akan diubah."
        )

    return all_jobs


def transform_jobs(all_jobs):
    """Mengubah respons GraphQL menjadi DataFrame."""

    rows = []

    for job in all_jobs:
        company = job.get("company") or {}
        province = job.get("province") or {}
        city = job.get("city") or {}
        job_role = job.get("jobRole") or {}

        rows.append({
            "job_id": job.get("id"),
            "job_code": job.get("code"),
            "job_title": job.get("positionName"),
            "company_name": company.get("name"),
            "company_code": company.get("code"),
            "location_province": province.get("name"),
            "location_city": city.get("name"),
            "job_role": job_role.get("displayName"),
            "education_level": job.get("educationLevelStr"),
            "salary_min": job.get("salaryLowerBound"),
            "salary_max": job.get("salaryUpperBound"),
            "experience": job.get("minExperience"),
            "job_type": job.get("typeStr"),
            "gender": job.get("genderStr"),
            "min_age": job.get("minAge"),
            "max_age": job.get("maxAge"),
            "updated_at": job.get("updatedAtStr"),
            "is_highlighted": job.get("isHighlighted"),
            "is_closed": job.get("isClosed"),
            "slug": job.get("slug")
        })

    df = pd.DataFrame(rows)

    df = df.drop_duplicates(subset="job_id")

    # Validasi data sebelum disimpan
    df = df.dropna(subset=["job_id"])

    if df.empty:
        raise RuntimeError(
            "Data hasil scraping tidak memiliki job_id yang valid. "
            "Dataset lama tidak akan diubah."
        )

    return df


def save_dataset(df, output_file=OUTPUT_FILE):
    """Menyimpan CSV dengan pengamanan terhadap kegagalan penulisan."""

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Tulis ke file sementara terlebih dahulu.
    temp_file = output_file.with_name(
        output_file.stem + ".tmp" + output_file.suffix
    )

    try:
        df.to_csv(
            temp_file,
            index=False,
            encoding="utf-8-sig"
        )

        # Mengganti dataset lama hanya setelah file baru berhasil ditulis.
        temp_file.replace(output_file)

    finally:
        if temp_file.exists():
            temp_file.unlink()

    log.info("Dataset berhasil disimpan: %s", output_file)
    log.info("Total data tersimpan: %s", len(df))


def main():
    try:
        all_jobs = scrape_jobs()
        df = transform_jobs(all_jobs)
        save_dataset(df)

        log.info("SCRAPING DATASET BERHASIL!")

    except Exception:
        log.exception(
            "Scraping gagal. Dataset sebelumnya tetap dipertahankan."
        )
        raise


if __name__ == "__main__":
    main()
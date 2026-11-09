"""Logika aplikasi (tanpa FastAPI agar mudah diuji)."""
import logging
import math
import re
from collections import Counter
from typing import Optional

import config
import llm
import matching as m
from knowledge_graph import ATTRIBUTES, JobKnowledgeGraph
from preprocessing import load_and_clean, to_records

log = logging.getLogger("service")

QUESTIONS = {
    "position": "Posisi pekerjaan apa yang kamu inginkan? Contohnya Sales, Marketing, atau Business Development.",
    "location": "Di kota atau daerah mana kamu ingin bekerja?",
    "education": "Apa pendidikan terakhir kamu? Contohnya SMA/SMK, D3/D4, S1, S2, atau S3.",
    "experience": "Berapa tahun pengalaman kerja yang kamu miliki? Jika belum memiliki pengalaman, jawab 0 tahun.",
    "jobType": "Jenis pekerjaan apa yang kamu inginkan? Contohnya Full-Time, Kontrak, Freelance, Part-Time, atau Magang.",
    "salaryMin": "Berapa gaji minimum yang kamu harapkan? Contohnya Rp5.000.000 atau 5 juta.",
    "gender": "Apa jenis kelamin yang ingin kamu pilih untuk kriteria lowongan? Jawab laki-laki, perempuan, atau semua.",
}

CRITERIA_TO_ATTR = {"position": "position", "location": "location", "education": "education",
                    "experience": "experience", "jobType": "job_type", "salaryMin": "salary",
                    "gender": "gender"}

class JobService:
    def __init__(self, csv_path=None):
        path = csv_path or config.CSV_PATH
        if not path.exists():
            log.warning("CSV %s tidak ditemukan -> memakai data contoh %s", path, config.SAMPLE_CSV_PATH)
            path = config.SAMPLE_CSV_PATH
        self.csv_path = path
        self.df = load_and_clean(path)
        self.records = to_records(self.df)
        self.by_id = {r["job_id"]: r for r in self.records}
        self.kg = JobKnowledgeGraph(self.records, config.SALARY_BASIS)

        cities = {re.sub(r"^(kota|kabupaten|kab)\s+", "", m.norm(r.get("location_city")))
                  for r in self.records if r.get("location_city")}
        self.known_locations = sorted(cities, key=len, reverse=True)  # frasa terpanjang dicoba dulu
        log.info("Knowledge Graph: %s", self.kg.stats())

    # ------------------------------------------------------------ serialisasi
    @staticmethod
    def to_public(rec: dict) -> dict:
        city, prov = rec.get("location_city_raw"), rec.get("location_province_raw")
        slug = rec.get("slug")
        return {
            "id": rec["job_id"],
            "title": rec.get("job_title_raw"),
            "role": rec.get("job_role_raw"),
            "company": rec.get("company_name_raw"),
            "city": city,
            "province": prov,
            "location": ", ".join(x for x in (city, prov) if x) or None,
            "education": rec.get("education_level_raw"),
            "experience": rec.get("experience"),
            "experienceMissing": bool(rec.get("experience_is_missing")),
            "jobType": rec.get("job_type_raw"),
            "gender": rec.get("gender_raw"),
            "salaryMin": rec.get("salary_min"),
            "salaryMax": rec.get("salary_max"),
            "maxAge": rec.get("max_age"),
            "updatedAt": rec.get("updated_at"),
            "highlighted": bool(rec.get("is_highlighted")),
            "closed": bool(rec.get("is_closed")),
            "slug": slug,
            "url": config.KITALULUS_JOB_URL.format(slug=slug) if slug else None,
        }

    # ------------------------------------------------------------ daftar lowongan
    def list_jobs(self, q="", location="", education="", experience=None, job_type="",
                  salary_min=None, gender="", include_closed=False, page=1, page_size=12) -> dict:
        q, loc = m.norm(q), m.norm(location)
        items = []
        for r in self.records:
            if r.get("is_closed") and not include_closed:
                continue
            if q and q not in m.norm(r.get("job_title")) and q not in m.norm(r.get("company_name")):
                continue
            if loc and not m.match_location(loc, ", ".join(x for x in (r.get("location_city"), r.get("location_province")) if x)):
                continue
            if education and not m.match_education(education, r.get("education_level")):
                continue
            if experience is not None and not m.match_experience(experience, r.get("experience")):
                continue
            if job_type and not m.match_job_type(job_type, r.get("job_type")):
                continue
            if salary_min is not None and not m.match_salary(salary_min, m.salary_reference(r, config.SALARY_BASIS)):
                continue
            if gender and not m.match_gender(gender, r.get("gender")):
                continue
            items.append(r)
        total = len(items)
        total_pages = max(1, math.ceil(total / page_size))
        page = min(max(1, page), total_pages)
        chunk = items[(page - 1) * page_size: page * page_size]
        return {"total": total, "page": page, "pageSize": page_size, "totalPages": total_pages,
                "items": [self.to_public(r) for r in chunk]}

    def get_job(self, job_id: str) -> Optional[dict]:
        rec = self.by_id.get(job_id)
        return self.to_public(rec) if rec else None

    def meta(self) -> dict:
        locs = {}
        for r in self.records:
            if r.get("location_city"):
                locs[r["location_city"]] = r.get("location_city_raw")
        types = {}
        for r in self.records:
            if r.get("job_type"):
                types[r["job_type"]] = r.get("job_type_raw")
        counts = Counter(r.get("location_city") for r in self.records if r.get("location_city"))
        return {
            "total": len(self.records),
            "locations": sorted(({"value": k, "label": v, "count": counts[k]} for k, v in locs.items()),
                                key=lambda x: x["label"] or ""),
            "jobTypes": sorted(({"value": k, "label": v} for k, v in types.items()), key=lambda x: x["label"] or ""),
        }

    # ----------------------------------------------------------------- asisten
    @staticmethod
    def missing(criteria: dict) -> list:
        return [k for k in llm.ORDER if criteria.get(k) is None or criteria.get(k) == ""]

    def chat(self, message: str, criteria: dict, asked: Optional[str]) -> dict:
        extracted, engine = llm.extract(message, criteria, asked, self.known_locations)
        updated = {k: v for k, v in extracted.items() if v is not None}
        merged = {**{k: criteria.get(k) for k in llm.ORDER}, **updated}
        missing = self.missing(merged)

        ack = ""
        if updated:
            ack = "Dicatat: " + "; ".join(f"{llm.LABELS[k]}: {self._fmt(k, v)}" for k, v in updated.items()) + ".\n\n"
        if missing:
            nxt = missing[0]
            reply = ack + QUESTIONS[nxt]
        else:
            nxt, reply = None, ack + "Semua kriteria sudah lengkap."
        if not updated and missing:
            reply = "Maaf, saya belum menangkap informasinya. " + QUESTIONS[nxt]
        return {"criteria": merged, "missing": missing, "complete": not missing,
                "asked": nxt, "reply": reply, "engine": engine}

    @staticmethod
    def _fmt(key, value):
        if key == "salaryMin":
            return "Rp" + f"{int(value):,}".replace(",", ".")
        if key == "experience":
            return f"{value} tahun"
        return value

    # ------------------------------------------------------------ rekomendasi
    def recommend(self, criteria: dict, limit: int = 20, include_closed: bool = False) -> dict:
        ranked = self.kg.recommend(criteria, include_closed)
        out = []
        for r in ranked[:limit]:
            job = self.to_public(self.by_id[r["job_id"]])
            job.update({
                "score": r["score"],
                "percentage": r["percentage"],
                "flags": r["flags"],
                "reasons": [m.REASON_TEXT[a] for a in ATTRIBUTES if r["flags"][a]],
            })
            out.append(job)
        return {"total": len(ranked), "returned": len(out), "attributes": len(ATTRIBUTES), "items": out}

"""Ekstraksi kriteria pengguna: Llama 3.2 (Ollama) + cadangan berbasis aturan."""
import json
import logging
import re
from typing import Optional

import requests

import config
import matching as m

log = logging.getLogger("llm")

ORDER = ["position", "location", "education", "experience", "jobType", "salaryMin", "gender"]
LABELS = {"position": "Posisi Pekerjaan", "location": "Lokasi", "education": "Pendidikan",
          "experience": "Pengalaman", "jobType": "Tipe Pekerjaan", "salaryMin": "Gaji Minimum",
          "gender": "Jenis Kelamin"}

SYSTEM_PROMPT = """Kamu adalah modul ekstraksi informasi untuk sistem rekomendasi lowongan kerja bidang penjualan dan bisnis.
Tugasmu HANYA mengubah pesan pengguna menjadi JSON dengan tepat 7 kunci berikut:

- "position"  : posisi yang dicari, huruf kecil (contoh: "sales", "marketing", "business development")
- "location"  : nama kota/daerah, huruf kecil (contoh: "tangerang", "jakarta selatan")
- "education" : salah satu dari "SD/Sederajat", "SMP/Sederajat", "SMA/SMK/Sederajat", "D3/D4", "S1", "S2", "S3"
- "experience": bilangan bulat, pengalaman dalam tahun ("fresh graduate", "belum berpengalaman" -> 0)
- "jobType"   : salah satu dari "Full-Time", "Part-Time", "Kontrak", "Freelance", "Magang"
- "salaryMin" : bilangan bulat dalam rupiah ("5 juta" -> 5000000, "Rp3.500.000" -> 3500000)
- "gender"    : salah satu dari "Laki-laki", "Perempuan", "Semua" ("Semua" jika pengguna tidak punya preferensi)

Aturan:
1. Isi nilai HANYA dari informasi yang disebutkan pengguna pada pesan terbaru.
2. Jika suatu informasi tidak disebutkan, isi dengan null. JANGAN menebak.
3. Jika pesan berupa jawaban singkat atas pertanyaan terakhir asisten, isi kunci yang ditanyakan itu.
4. Keluarkan JSON saja, tanpa penjelasan dan tanpa teks lain."""


# ------------------------------------------------------------------ Ollama
def ollama_available() -> bool:
    try:
        return requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=1.5).ok
    except requests.RequestException:
        return False


def _call_ollama(message: str, current: dict, asked: Optional[str]) -> dict:
    known = {k: v for k, v in current.items() if v is not None}
    user_prompt = (
        f"Informasi yang sudah diketahui: {json.dumps(known, ensure_ascii=False)}\n"
        f"Pertanyaan terakhir asisten: {LABELS.get(asked, '(tidak ada)')}\n"
        f'Pesan pengguna: "{message}"\n\nKeluarkan JSON dengan 7 kunci.'
    )
    resp = requests.post(
        f"{config.OLLAMA_URL}/api/chat",
        json={
            "model": config.OLLAMA_MODEL,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                         {"role": "user", "content": user_prompt}],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        },
        timeout=config.OLLAMA_TIMEOUT,
    )
    resp.raise_for_status()
    data = json.loads(resp.json()["message"]["content"])
    if not isinstance(data, dict):
        raise ValueError("Keluaran Llama bukan objek JSON")
    return data


# ------------------------------------------------------- validasi keluaran
def _clean(v):
    if v is None:
        return None
    if isinstance(v, str) and v.strip().lower() in {"", "null", "none", "n/a", "tidak ada"}:
        return None
    return v


def sanitize(raw: dict) -> dict:
    """Validasi + normalisasi keluaran model ke format kanonik (null jika tidak valid)."""
    out = {k: None for k in ORDER}
    pos = _clean(raw.get("position"))
    if isinstance(pos, str): out["position"] = m.norm(pos) or None
    loc = _clean(raw.get("location"))
    if isinstance(loc, str): out["location"] = re.sub(r"^di\s+", "", m.norm(loc)) or None
    edu = _clean(raw.get("education"))
    if edu is not None: out["education"] = m.canonical_education(edu)
    exp = _clean(raw.get("experience"))
    if exp is not None: out["experience"] = m.parse_experience(exp)
    jt = m.canonical_job_type(_clean(raw.get("jobType")))
    out["jobType"] = m.JOB_TYPE_LABELS.get(jt)
    sal = _clean(raw.get("salaryMin"))
    if sal is not None: out["salaryMin"] = m.parse_salary(sal)
    g = m.canonical_gender(_clean(raw.get("gender")))
    out["gender"] = m.GENDER_LABELS.get(g)
    return out


# ------------------------------------------------------ cadangan (aturan)
POSITION_KEYWORDS = [
    "business development", "account executive", "account manager", "sales executive",
    "sales representative", "key account", "relationship officer", "digital marketing",
    "trade marketing", "telemarketing", "telesales", "marketing", "sales", "promotor",
    "partnership", "merchant", "commercial", "retail", "e-commerce",
]


def extract_with_rules(message: str, asked: Optional[str] = None,
                       known_locations: Optional[list] = None) -> dict:
    text = m.norm(message)
    out = {k: None for k in ORDER}

    out["position"] = next((p for p in POSITION_KEYWORDS if m.norm(p) in text), None)

    for loc in known_locations or []:
        if re.search(rf"\b{re.escape(loc)}\b", text):
            out["location"] = loc
            break

    out["education"] = m.canonical_education(text)
    out["experience"] = m.parse_experience(text) if re.search(
        r"\d+\s*(tahun|thn)|fresh graduate|belum|tanpa pengalaman", text) else None
    jt = m.canonical_job_type(text)
    out["jobType"] = m.JOB_TYPE_LABELS.get(jt)   # None jika tidak ada kata kunci tipe pekerjaan
    if re.search(r"(juta|jt|ribu|rb)\b|\d{6,}", message.lower().replace(".", "")):
        out["salaryMin"] = m.parse_salary(message.lower())
    if re.search(r"semua|bebas|tidak ada preferensi|laki|pria|perempuan|wanita", text):
        out["gender"] = m.GENDER_LABELS.get(m.canonical_gender(text))

    # jawaban singkat untuk pertanyaan yang sedang ditanyakan
    if asked and out.get(asked) is None:
        short = message.strip()
        if asked == "position" and len(short) <= 40:
            out["position"] = m.norm(short) or None
        elif asked == "location" and len(short) <= 40:
            out["location"] = re.sub(r"^di\s+", "", m.norm(short)) or None
        elif asked == "experience" and re.fullmatch(r"\d+", short):
            out["experience"] = int(short)
    return out


# --------------------------------------------------------------- gabungan
def extract(message: str, current: dict, asked: Optional[str],
            known_locations: Optional[list] = None) -> tuple[dict, str]:
    rules = extract_with_rules(message, asked, known_locations)
    if not config.USE_LLM:
        return rules, "rule-based"
    try:
        out = sanitize(_call_ollama(message, current, asked))
    except Exception as exc:  # Ollama mati / timeout / JSON rusak
        log.warning("Ekstraksi Llama gagal (%s); memakai aturan.", exc)
        return rules, "rule-based"

    # angka gaji diparse deterministik: model kecil sering keliru mengonversi "juta"
    if rules.get("salaryMin") is not None:
        out["salaryMin"] = rules["salaryMin"]
    # jawaban untuk pertanyaan yang sedang ditanyakan tidak boleh hilang
    if asked and out.get(asked) is None and rules.get(asked) is not None:
        out[asked] = rules[asked]
    return out, config.OLLAMA_MODEL

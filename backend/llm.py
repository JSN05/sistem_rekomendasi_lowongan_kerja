"""Ekstraksi kriteria pengguna: Llama 3.2 (Ollama) + cadangan berbasis aturan."""
import json
import logging
import re
import requests
import config
import matching as m
from typing import Optional

log = logging.getLogger("llm")

ORDER = ["position", "location", "education", "experience", "jobType", "salaryMin", "gender"]
LABELS = {"position": "Posisi Pekerjaan", "location": "Lokasi", "education": "Pendidikan",
          "experience": "Pengalaman", "jobType": "Tipe Pekerjaan", "salaryMin": "Gaji Minimum",
          "gender": "Jenis Kelamin"}

SYSTEM_PROMPT = """Kamu adalah modul ekstraksi informasi untuk sistem rekomendasi lowongan kerja bidang penjualan dan bisnis.
Tugasmu adalah mengekstrak informasi dari pesan terbaru pengguna menjadi JSON dengan tepat 7 kunci berikut:

- "position": posisi pekerjaan yang dicari, huruf kecil.
  Contoh: "sales", "sales manager", "marketing", "business development".
- "location": nama kota atau daerah, huruf kecil.
  Contoh: "jakarta", "bandung", "jakarta selatan".
- "education": salah satu dari "SD/Sederajat", "SMP/Sederajat", "SMA/SMK/Sederajat", "D3/D4", "S1", "S2", "S3".
- "experience": bilangan bulat dalam tahun. "fresh graduate" atau "belum berpengalaman" berarti 0.
- "jobType": salah satu dari "Full-Time", "Part-Time", "Kontrak", "Freelance", "Magang".
- "salaryMin": bilangan bulat dalam rupiah. Contoh: "5 juta" berarti 5000000.
- "gender": salah satu dari "Laki-laki", "Perempuan", "Semua".

ATURAN EKSTRAKSI:

1. Ekstrak hanya informasi yang disebutkan atau dapat dipahami secara jelas dari pesan TERBARU pengguna.
2. Jika informasi tidak disebutkan, isi dengan null. Jangan menebak atau menyalin nilai lama dari informasi yang sudah diketahui.
3. Jika pengguna memberikan informasi baru untuk kriteria yang sudah pernah diisi, keluarkan nilai baru tersebut. Nilai baru akan menggantikan nilai sebelumnya.
4. Kenali instruksi perubahan seperti:
   - "Ganti lokasi saya menjadi Bandung."
   - "Saya ingin posisi Marketing, bukan Sales."
   - "Ubah gaji minimum menjadi 7 juta."
   - "Sekarang saya ingin pekerjaan Full-Time."
5. Jika pengguna menjawab pertanyaan terakhir asisten secara singkat, masukkan jawabannya ke kunci yang sedang ditanyakan.
6. Jika pengguna menyebutkan beberapa kriteria sekaligus, ekstrak semuanya.
7. Jangan mengubah kriteria yang tidak disebutkan pengguna.
8. Jangan menganggap pengguna ingin memulai pencarian baru hanya karena memberikan perubahan kriteria.
9. Jika pengguna secara eksplisit tidak memiliki preferensi gender, gunakan "Semua".
10. Jika informasi tidak cukup jelas untuk menentukan nilai, gunakan null.

Keluarkan JSON valid dengan tepat 7 kunci tersebut.
Jangan berikan penjelasan, Markdown, atau teks lain di luar JSON."""

def ollama_available() -> bool:
    try:
        return requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=1.5).ok
    except requests.RequestException:
        return False

def _call_ollama(message: str, current: dict, asked: Optional[str]) -> dict:
    known = {k: v for k, v in current.items() if v is not None}
    user_prompt = (
        f"Kriteria yang saat ini tersimpan: "
        f"{json.dumps(known, ensure_ascii=False)}\n"
        f"Pertanyaan terakhir asisten: "
        f"{LABELS.get(asked, '(tidak ada)')}\n"
        f"Pesan terbaru pengguna: \"{message}\"\n\n"
        "Ekstrak hanya informasi baru atau perubahan yang disebutkan "
        "dalam pesan terbaru pengguna.\n"
        "Jika pengguna mengubah kriteria lama, keluarkan nilai barunya.\n"
        "Jika tidak ada informasi baru untuk suatu kriteria, isi null.\n"
        "Jangan menyalin nilai lama.\n\n"
        "Keluarkan JSON dengan tepat 7 kunci."
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

    out["position"] = next(
        (p for p in POSITION_KEYWORDS if m.norm(p) in text),
        None
    )

    for loc in known_locations or []:
        loc_norm = m.norm(loc)
        if re.search(rf"\b{re.escape(loc_norm)}\b", text):
            out["location"] = loc_norm
            break

    if out["location"] is None:
        location_match = re.search(
            r"\b(?:di|kota|daerah|wilayah)\s+"
            r"([a-z]+(?:\s+[a-z]+){0,2})",
            text
        )

        if location_match:
            candidate = location_match.group(1).strip()

            candidate = re.split(
                r"\b(?:dengan|dan|gaji|pendidikan|pengalaman|"
                r"jenis|kelamin|tipe|pekerjaan|minimal)\b",
                candidate
            )[0].strip()

            if candidate:
                out["location"] = candidate

    out["education"] = m.canonical_education(text)

    out["experience"] = (
        m.parse_experience(text)
        if re.search(
            r"\d+\s*(tahun|thn)|fresh graduate|belum|tanpa pengalaman",
            text
        )
        else None
    )

    jt = m.canonical_job_type(text)
    out["jobType"] = m.JOB_TYPE_LABELS.get(jt)

    if re.search(
        r"(juta|jt|ribu|rb)\b|\d{6,}",
        message.lower().replace(".", "")
    ):
        out["salaryMin"] = m.parse_salary(message.lower())

    if re.search(
        r"semua|bebas|tidak ada preferensi|laki|pria|perempuan|wanita",
        text
    ):
        out["gender"] = m.GENDER_LABELS.get(m.canonical_gender(text))

    if asked and out.get(asked) is None:
        short = message.strip()
        if asked == "position" and len(short) <= 40:
            out["position"] = m.norm(short) or None
        elif asked == "location" and len(short) <= 40:
            out["location"] = re.sub(r"^di\s+", "", m.norm(short)) or None
        elif asked == "experience" and re.fullmatch(r"\d+", short):
            out["experience"] = int(short)
    return out

def extract(message: str, current: dict, asked: Optional[str],
            known_locations: Optional[list] = None) -> tuple[dict, str]:
    rules = extract_with_rules(message, asked, known_locations)
    if not config.USE_LLM:
        return rules, "rule-based"
    try:
        out = sanitize(_call_ollama(message, current, asked))
    except Exception as exc:
        log.warning("Ekstraksi Llama gagal (%s); memakai aturan.", exc)
        return rules, "rule-based"

    for key in ORDER:
        if out.get(key) is None and rules.get(key) is not None:
            out[key] = rules[key]
    return out, config.OLLAMA_MODEL
"""Normalisasi nilai + aturan pencocokan satu atribut (hasil 1 atau 0, Bab 2.5 paper)."""
import re
from typing import Optional


def norm(text) -> str:
    if text is None:
        return ""
    s = str(text).lower().strip()
    s = re.sub(r"[-_/]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- pendidikan
EDU_LABELS = {1: "SD/Sederajat", 2: "SMP/Sederajat", 3: "SMA/SMK/Sederajat",
              4: "D3/D4", 5: "S1", 6: "S2", 7: "S3"}


def education_level(text) -> Optional[int]:
    """0 = semua jenjang, 1..7 = SD..S3, None = tidak dikenali."""
    t = norm(text)
    if not t:
        return None
    if "semua" in t or "tidak ada" in t:
        return 0
    levels = set()
    if re.search(r"\bs3\b|doktor", t): levels.add(7)
    if re.search(r"\bs2\b|magister", t): levels.add(6)
    if re.search(r"\bs1\b|sarjana", t): levels.add(5)
    if re.search(r"\bd[1-4]\b|diploma", t): levels.add(4)
    if re.search(r"\bsma\b|\bsmk\b|\bslta\b|\bma\b", t): levels.add(3)
    if re.search(r"\bsmp\b|\bmts\b|\bsltp\b", t): levels.add(2)
    if re.search(r"\bsd\b|sekolah dasar", t): levels.add(1)
    return min(levels) if levels else None


def canonical_education(text) -> Optional[str]:
    level = education_level(text)
    return EDU_LABELS.get(level) if level else None


# -------------------------------------------------------------- tipe pekerjaan
JOB_TYPE_LABELS = {"full time": "Full-Time", "part time": "Part-Time", "kontrak": "Kontrak",
                   "freelance": "Freelance", "magang": "Magang"}


def canonical_job_type(text) -> str:
    t = norm(text).replace("fulltime", "full time").replace("parttime", "part time")
    if not t:
        return ""
    if "full time" in t: return "full time"
    if "part time" in t: return "part time"
    if "freelance" in t: return "freelance"
    if "kontrak" in t or "contract" in t: return "kontrak"
    if "magang" in t or "intern" in t: return "magang"
    return t


# --------------------------------------------------------------------- gender
GENDER_LABELS = {"laki laki": "Laki-laki", "perempuan": "Perempuan", "semua": "Semua"}


def canonical_gender(text, job: bool = False) -> str:
    """job=True: lowongan tanpa syarat gender dianggap terbuka untuk semua."""
    t = norm(text)
    if not t:
        return "semua" if job else ""
    has_l = bool(re.search(r"laki|pria", t))
    has_p = bool(re.search(r"perempuan|wanita", t))
    if "semua" in t or "tidak ada" in t or "bebas" in t or (has_l and has_p):
        return "semua"
    if has_l: return "laki laki"
    if has_p: return "perempuan"
    return "semua" if job else t


# ------------------------------------------------------------ angka (gaji, dll)
def parse_salary(value) -> Optional[int]:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(value)
    t = str(value).lower().strip()
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:juta|jt)\b", t)
    if m:
        return int(round(float(m.group(1).replace(",", ".")) * 1_000_000))
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:ribu|rb|k)\b", t)
    if m:
        return int(round(float(m.group(1).replace(",", ".")) * 1_000))
    tokens = re.findall(r"\d[\d.,]*\d|\d", t)
    for tok in tokens:                      # ambil angka >= 6 digit ("Rp5.000.000")
        digits = re.sub(r"\D", "", tok)
        if len(digits) >= 6:
            return int(digits)
    return int(re.sub(r"\D", "", tokens[0])) if len(tokens) == 1 else None


def parse_experience(value) -> Optional[int]:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(value)
    t = norm(value)
    if re.search(r"fresh graduate|belum (punya|berpengalaman|ada)|tanpa pengalaman", t):
        return 0
    m = re.search(r"(\d+)\s*(?:tahun|thn|th)\b", t)
    if m:
        return int(m.group(1))
    return int(t) if re.fullmatch(r"\d+", t) else None


def salary_reference(rec: dict, basis: str = "min") -> Optional[int]:
    """Nilai gaji lowongan yang dibandingkan dengan gaji minimum pengguna."""
    key = "salary_max" if basis == "max" else "salary_min"
    return rec.get(key)


# ------------------------------------------------------------------ predikat
POSITION_SYNONYMS = {
    "business development": ["business development", "bizdev", "biz dev"],
    "bizdev": ["business development", "bizdev", "biz dev"],
    "telemarketing": ["telemarketing", "tele marketing"],
    "telesales": ["telesales", "tele sales"],
    "e commerce": ["e commerce", "ecommerce"],
}


def match_position(user_position, job_title) -> bool:
    p, t = norm(user_position), norm(job_title)
    if not p or not t:
        return False
    if any(c in t for c in {p, *POSITION_SYNONYMS.get(p, [])}):
        return True
    tokens = [w for w in p.split() if len(w) > 2]
    return bool(tokens) and all(w in t for w in tokens)


def match_location(user_location, job_location) -> bool:
    u = re.sub(r"^(di|kota|kabupaten|kab)\s+", "", norm(user_location))
    j = norm(job_location)
    return bool(u) and bool(j) and u in j


def match_education(user_education, job_education) -> bool:
    ul, jl = education_level(user_education), education_level(job_education)
    if jl is None:          # persyaratan tidak diketahui
        return False
    if jl == 0:             # "Semua Jenjang"
        return True
    return ul is not None and ul >= jl


def match_experience(user_exp, job_exp) -> bool:
    if user_exp is None:
        return False
    return int(user_exp) >= int(job_exp or 0)


def match_job_type(user_type, job_type) -> bool:
    u, j = canonical_job_type(user_type), canonical_job_type(job_type)
    return bool(u) and u == j


def match_salary(user_salary, job_salary) -> bool:
    if user_salary is None or job_salary is None:
        return False
    return int(job_salary) >= int(user_salary)


def match_gender(user_gender, job_gender) -> bool:
    u, j = canonical_gender(user_gender), canonical_gender(job_gender, job=True)
    return bool(u) and (u == "semua" or j == "semua" or u == j)


REASON_TEXT = {
    "position": "Posisi pekerjaan sesuai",
    "location": "Lokasi pekerjaan sesuai",
    "education": "Pendidikan memenuhi persyaratan",
    "experience": "Pengalaman kerja memenuhi persyaratan",
    "job_type": "Tipe pekerjaan sesuai",
    "salary": "Gaji memenuhi harapan minimum",
    "gender": "Persyaratan jenis kelamin sesuai",
}

"""FastAPI: menghubungkan frontend dengan sistem rekomendasi.

Jalankan:  uvicorn main:app --reload --port 8000
"""
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import config
import llm
from service import JobService

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["svc"] = JobService()      # baca CSV -> pra-proses -> bangun Knowledge Graph (sekali saja)
    yield


app = FastAPI(title="Sistem Rekomendasi Lowongan Kerja (LLM + Knowledge Graph)", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS,
                   allow_methods=["*"], allow_headers=["*"])


def svc() -> JobService:
    return state["svc"]


# Nama field memakai camelCase agar sama persis dengan kunci di frontend.
class Criteria(BaseModel):
    position: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[int] = Field(None, ge=0, le=60)
    jobType: Optional[str] = None
    salaryMin: Optional[int] = Field(None, ge=0)
    gender: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    criteria: Criteria = Criteria()
    asked: Optional[str] = None


class RecommendRequest(BaseModel):
    criteria: Criteria
    limit: int = Field(20, ge=1, le=100)
    include_closed: bool = False


@app.get("/api/health")
def health():
    s = svc()
    return {"status": "ok", "jobs": len(s.records), "csv": s.csv_path.name,
            "graph": s.kg.stats(), "ollama": llm.ollama_available(), "model": config.OLLAMA_MODEL}


@app.get("/api/meta")
def meta():
    return svc().meta()


@app.get("/api/jobs")
def list_jobs(
    q: str = "", location: str = "", education: str = "",
    experience: Optional[int] = Query(None, ge=0), job_type: str = "",
    salary_min: Optional[int] = Query(None, ge=0), gender: str = "",
    include_closed: bool = False,
    page: int = Query(1, ge=1), page_size: int = Query(12, ge=1, le=50),
):
    return svc().list_jobs(q, location, education, experience, job_type, salary_min,
                           gender, include_closed, page, page_size)


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = svc().get_job(job_id)
    if not job:
        raise HTTPException(404, "Lowongan tidak ditemukan")
    return job


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Ekstraksi kriteria dari bahasa alami (Llama 3.2) + pertanyaan lanjutan jika belum lengkap."""
    return svc().chat(req.message, req.criteria.model_dump(), req.asked)


@app.post("/api/recommend")
def recommend(req: RecommendRequest):
    criteria = req.criteria.model_dump()
    missing = svc().missing(criteria)
    if missing:
        raise HTTPException(422, {"message": "Kriteria belum lengkap", "missing": missing})
    return svc().recommend(criteria, req.limit, req.include_closed)


@app.get("/")
def root():
    return RedirectResponse("/beranda.html")


# Sajikan frontend dari backend yang sama -> http://localhost:8000/beranda.html
if config.FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=config.FRONTEND_DIR, html=True), name="frontend")

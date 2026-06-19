from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ats, jobs, resumes, search, upload
from app.services.embedding_service import MODEL_NAME

app = FastAPI(
    title="Local AI Recruiting ATS",
    description="Portfolio ATS powered by free local/open-source AI models.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=os.getenv("ATS_CORS_ORIGIN_REGEX", r"https://.*\.(up\.railway\.app|vercel\.app)"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumes.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(ats.router, prefix="/api")
app.include_router(upload.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "service": "Local AI Recruiting ATS API"}


@app.get("/health")
def railway_health():
    return {"status": "ok"}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mode": "local-free-ai",
        "embedding_model": MODEL_NAME,
        "workflow_engine": "LangGraph StateGraph",
        "paid_apis": False,
    }

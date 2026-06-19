from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from app.models import JobDescription, Resume, UploadStatus


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
RESUMES_PATH = DATA_DIR / "resumes.json"
JOBS_PATH = DATA_DIR / "jobs.json"

_lock = Lock()
_upload_status: dict[str, UploadStatus] = {}


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any) -> Any:
    ensure_data_dir()
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, payload: Any) -> None:
    ensure_data_dir()
    with _lock:
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)


def load_resumes() -> list[Resume]:
    return [Resume(**item) for item in read_json(RESUMES_PATH, [])]


def save_resumes(resumes: list[Resume]) -> None:
    write_json(RESUMES_PATH, [resume.model_dump() for resume in resumes])


def append_resumes(new_resumes: list[Resume]) -> None:
    resumes = load_resumes()
    existing_ids = {resume.id for resume in resumes}
    merged = resumes + [resume for resume in new_resumes if resume.id not in existing_ids]
    save_resumes(merged)


def load_jobs() -> list[JobDescription]:
    return [JobDescription(**item) for item in read_json(JOBS_PATH, [])]


def save_jobs(jobs: list[JobDescription]) -> None:
    write_json(JOBS_PATH, [job.model_dump() for job in jobs])


def get_job(job_id: str) -> JobDescription | None:
    return next((job for job in load_jobs() if job.id == job_id), None)


def get_resume(resume_id: str) -> Resume | None:
    return next((resume for resume in load_resumes() if resume.id == resume_id), None)


def set_upload_status(status: UploadStatus) -> None:
    _upload_status[status.batch_id] = status


def get_upload_status(batch_id: str) -> UploadStatus | None:
    return _upload_status.get(batch_id)


def list_upload_statuses() -> list[UploadStatus]:
    return list(_upload_status.values())

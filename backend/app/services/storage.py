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
    seed_demo_data_if_missing()
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, payload: Any) -> None:
    ensure_data_dir()
    with _lock:
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)


def seed_demo_data_if_missing() -> None:
    if RESUMES_PATH.exists() and JOBS_PATH.exists():
        return
    try:
        import random

        from scripts.generate_mock_data import JOB_SPECS, _job, _resume
    except Exception:
        return

    random.seed(42)
    with _lock:
        if not RESUMES_PATH.exists():
            resumes = [_resume(index) for index in range(1, 1001)]
            RESUMES_PATH.write_text(json.dumps(resumes, indent=2), encoding="utf-8")
        if not JOBS_PATH.exists():
            jobs = [
                _job(index, title, skills, location, compensation, domain)
                for index, (title, skills, location, compensation, domain) in enumerate(JOB_SPECS, start=1)
            ]
            JOBS_PATH.write_text(json.dumps(jobs, indent=2), encoding="utf-8")


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

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models import JobDescription, ParsedJD
from app.services.jd_parser import parse_jd
from app.services.storage import get_job, load_jobs, save_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobCreateRequest(BaseModel):
    title: str
    description: str
    required_skills: list[str] = []


class JDParseRequest(BaseModel):
    description: str
    required_skills: list[str] = []


@router.get("", response_model=list[JobDescription])
def list_jobs():
    return load_jobs()


@router.post("", response_model=JobDescription)
def create_job(payload: JobCreateRequest):
    jobs = load_jobs()
    job = JobDescription(
        id=f"job-{len(jobs) + 1:03d}",
        title=payload.title,
        description=payload.description,
        required_skills=payload.required_skills or parse_jd(payload.description).required_skills,
    )
    jobs.append(job)
    save_jobs(jobs)
    return job


@router.post("/parse", response_model=ParsedJD)
def parse_job_description(payload: JDParseRequest):
    return parse_jd(payload.description, payload.required_skills)


@router.get("/{job_id}", response_model=JobDescription)
def job_detail(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/parsed", response_model=ParsedJD)
def parsed_job(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return parse_jd(job.description, job.required_skills)

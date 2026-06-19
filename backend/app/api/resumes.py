from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.models import Resume, UploadStatus
from app.services.storage import get_resume, list_upload_statuses, load_resumes

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("", response_model=list[Resume])
def list_resumes(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    resumes = load_resumes()
    return resumes[offset : offset + limit]


@router.get("/stats")
def resume_stats():
    resumes = load_resumes()
    skills = sorted({skill for resume in resumes for skill in resume.skills})
    avg_exp = round(sum(resume.experience for resume in resumes) / max(len(resumes), 1), 1)
    return {"total": len(resumes), "skills": skills, "average_experience": avg_exp}


@router.get("/uploads", response_model=list[UploadStatus])
def upload_statuses():
    return list_upload_statuses()


@router.get("/{resume_id}", response_model=Resume)
def resume_detail(resume_id: str):
    resume = get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

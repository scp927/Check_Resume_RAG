from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models import ATSRunRequest, ATSRunResponse, JDResumeCheckRequest, JDResumeCheckResponse
from app.services.langgraph_workflow import check_jd_resume, run_ats_workflow, stream_ats_workflow

router = APIRouter(prefix="/ats", tags=["ats"])


@router.post("/run", response_model=ATSRunResponse)
def run_ats(payload: ATSRunRequest):
    try:
        return run_ats_workflow(
            job_id=payload.job_id,
            job_description=payload.job_description,
            resume_ids=payload.resume_ids,
            top_k=payload.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/run/stream")
def stream_ats(payload: ATSRunRequest):
    def events():
        try:
            for event in stream_ats_workflow(
                job_id=payload.job_id,
                job_description=payload.job_description,
                resume_ids=payload.resume_ids,
                top_k=payload.top_k,
            ):
                yield json.dumps(event, default=str) + "\n"
        except ValueError as exc:
            yield json.dumps({"type": "error", "message": str(exc)}) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")


@router.post("/check", response_model=JDResumeCheckResponse)
def check_resume_against_jd(payload: JDResumeCheckRequest):
    return check_jd_resume(
        job_description=payload.job_description,
        resume_text=payload.resume_text,
        resume_name=payload.resume_name,
        resume_skills=payload.resume_skills,
        experience=payload.experience,
    )

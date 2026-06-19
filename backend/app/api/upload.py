from __future__ import annotations

import re
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, UploadFile

from app.models import Resume, UploadStatus
from app.services.document_parser import extract_text
from app.services.jd_parser import SKILL_ALIASES
from app.services.search_service import get_search_service
from app.services.storage import append_resumes, get_upload_status, set_upload_status

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/resumes", response_model=UploadStatus)
async def upload_resumes(background_tasks: BackgroundTasks, files: list[UploadFile] = File(...)):
    batch_id = str(uuid.uuid4())
    payloads = [(file.filename or "resume.txt", await file.read()) for file in files]
    status = UploadStatus(
        batch_id=batch_id,
        status="queued",
        total=len(payloads),
        processed=0,
        message="Resume batch queued for local processing.",
    )
    set_upload_status(status)
    background_tasks.add_task(_process_uploads, batch_id, payloads)
    return status


@router.get("/status/{batch_id}", response_model=UploadStatus)
def upload_status(batch_id: str):
    return get_upload_status(batch_id) or UploadStatus(
        batch_id=batch_id,
        status="unknown",
        total=0,
        processed=0,
        message="Batch not found.",
    )


def _process_uploads(batch_id: str, payloads: list[tuple[str, bytes]]) -> None:
    resumes: list[Resume] = []
    total = len(payloads)
    set_upload_status(UploadStatus(batch_id=batch_id, status="processing", total=total, processed=0, message="Extracting text."))
    for index, (filename, content) in enumerate(payloads, start=1):
        text = extract_text(filename, content)
        resumes.append(
            Resume(
                id=f"uploaded-{batch_id[:8]}-{index:03d}",
                name=_name_from_filename(filename),
                skills=_extract_skills(text),
                experience=_extract_experience(text),
                education=_extract_education(text),
                raw_text=text,
            )
        )
        set_upload_status(
            UploadStatus(
                batch_id=batch_id,
                status="processing",
                total=total,
                processed=index,
                message=f"Processed {index} of {total} resumes.",
            )
        )
    append_resumes(resumes)
    get_search_service().rebuild()
    set_upload_status(
        UploadStatus(
            batch_id=batch_id,
            status="complete",
            total=total,
            processed=total,
            message="Batch indexed in local FAISS search.",
        )
    )


def _name_from_filename(filename: str) -> str:
    stem = Path(filename).stem.replace("_", " ").replace("-", " ")
    return " ".join(part.capitalize() for part in stem.split()) or "Uploaded Candidate"


def _extract_skills(text: str) -> list[str]:
    lower = text.lower()
    skills = [label for needle, label in SKILL_ALIASES.items() if needle in lower]
    return sorted(set(skills))


def _extract_experience(text: str) -> int:
    matches = re.findall(r"(\d+)\+?\s*(?:years|yrs|yr)", text.lower())
    return max([int(match) for match in matches], default=2)


def _extract_education(text: str) -> str:
    lower = text.lower()
    if "phd" in lower or "doctorate" in lower:
        return "PhD"
    if "master" in lower or "msc" in lower:
        return "Master's"
    if "bachelor" in lower or "bs " in lower or "ba " in lower:
        return "Bachelor's"
    return "Not specified"

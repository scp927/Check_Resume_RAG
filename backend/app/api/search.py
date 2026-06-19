from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models import LangGraphSearchRequest, LangGraphSearchResponse, SearchRequest, SearchResult
from app.services.langgraph_workflow import run_search_workflow, stream_search_workflow
from app.services.search_service import get_search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=list[SearchResult])
def semantic_search(payload: SearchRequest):
    return get_search_service().search(payload.query, payload.top_k)


@router.post("/langgraph", response_model=LangGraphSearchResponse)
def langgraph_search(payload: LangGraphSearchRequest):
    return run_search_workflow(
        query=payload.query,
        job_description=payload.job_description,
        top_k=payload.top_k,
        max_iterations=payload.max_iterations,
        validation_threshold=payload.validation_threshold,
    )


@router.post("/langgraph/stream")
def stream_langgraph_search(payload: LangGraphSearchRequest):
    def events():
        for event in stream_search_workflow(
            query=payload.query,
            job_description=payload.job_description,
            top_k=payload.top_k,
            max_iterations=payload.max_iterations,
            validation_threshold=payload.validation_threshold,
        ):
            yield json.dumps(event, default=str) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")


@router.post("/rebuild")
def rebuild_index():
    get_search_service().rebuild()
    return {"status": "rebuilt"}

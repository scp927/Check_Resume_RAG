from __future__ import annotations

import os
import re
from collections.abc import Iterator
from functools import lru_cache
from typing import Any, TypedDict

import numpy as np

from app.models import ATSRunResponse, CandidateScore, JDResumeCheckResponse, JobDescription, LangGraphSearchResponse, ParsedJD, Resume, WorkflowStep
from app.services.ats_engine import rank_candidates, score_candidate
from app.services.embedding_service import get_embedding_service
from app.services.jd_parser import SKILL_ALIASES
from app.services.jd_parser import parse_jd
from app.services.search_service import get_search_service
from app.services.storage import get_job, load_resumes


class ATSState(TypedDict, total=False):
    job_id: str | None
    job_description: str | None
    resume_ids: list[str] | None
    top_k: int
    job: JobDescription | None
    parsed_jd: ParsedJD
    resumes: list[Resume]
    similarities: dict[str, float]
    candidates: list[Any]
    leaderboard: list[Any]
    report: dict[str, Any]


class SearchWorkflowState(TypedDict, total=False):
    query: str
    job_description: str | None
    current_query: str
    top_k: int
    max_iterations: int
    validation_threshold: float
    parsed_jd: ParsedJD
    iteration: int
    retrieved: list[Any]
    ranked: list[CandidateScore]
    best_ranked: list[CandidateScore]
    best_validation: float
    validated: bool
    steps: list[WorkflowStep]


def run_ats_workflow(
    job_id: str | None = None,
    job_description: str | None = None,
    resume_ids: list[str] | None = None,
    top_k: int = 25,
) -> ATSRunResponse:
    initial_state: ATSState = {
        "job_id": job_id,
        "job_description": job_description,
        "resume_ids": resume_ids,
        "top_k": top_k,
    }
    final_state = get_compiled_ats_graph().invoke(initial_state)
    return ATSRunResponse(
        job=final_state.get("job"),
        parsed_jd=final_state["parsed_jd"],
        candidate_count=len(final_state["leaderboard"]),
        leaderboard=final_state["leaderboard"][:top_k],
        process_visibility=final_state["report"],
    )


def stream_ats_workflow(
    job_id: str | None = None,
    job_description: str | None = None,
    resume_ids: list[str] | None = None,
    top_k: int = 25,
) -> Iterator[dict[str, Any]]:
    state: ATSState = {
        "job_id": job_id,
        "job_description": job_description,
        "resume_ids": resume_ids,
        "top_k": top_k,
    }
    steps: list[WorkflowStep] = []

    for node_name, message, node in (
        ("load_jd", "Loading selected job description into the LangGraph ATS workflow.", _load_jd),
        ("parse_jd", "Parsing the JD into required skills, experience level, and domain keywords.", _parse_jd_node),
        ("load_resumes", "Loading the selected resume batch for ATS scoring.", _load_resumes_node),
        ("generate_embeddings", "Building or loading MiniLM resume embeddings and FAISS index.", _generate_embeddings_node),
        ("semantic_retrieval", "Calculating semantic similarity between the JD and resumes.", _semantic_retrieval_node),
        ("ats_scoring", "Scoring candidates with semantic, skill, experience, and keyword signals.", _score_candidates_node),
        ("ranking_engine", "Ranking candidates by ATS score, semantic similarity, and skill match ratio.", _ranking_node),
        ("generate_report", "Generating recruiter-visible explanation and score breakdown report.", _report_node),
    ):
        running_step = WorkflowStep(step=node_name, status="running", message=message)
        steps.append(running_step)
        yield {"type": "step", "step": running_step.model_dump()}
        state = node(state)
        completed_step = WorkflowStep(
            step=node_name,
            status="complete",
            message=_ats_completed_message(node_name, state),
            details=_ats_step_details(node_name, state),
        )
        steps[-1] = completed_step
        yield {"type": "step_update", "step": completed_step.model_dump()}

    response = ATSRunResponse(
        job=state.get("job"),
        parsed_jd=state["parsed_jd"],
        candidate_count=len(state["leaderboard"]),
        leaderboard=state["leaderboard"][:top_k],
        process_visibility={**state["report"], "workflow_steps": [step.model_dump() for step in steps]},
    )
    final_step = WorkflowStep(
        step="finalize",
        status="complete",
        message="LangGraph ATS workflow complete. Final leaderboard and score breakdown are ready.",
        details={"candidate_count": response.candidate_count, "returned": len(response.leaderboard)},
    )
    yield {"type": "final", "step": final_step.model_dump(), "result": response.model_dump()}


def stream_search_workflow(
    query: str,
    job_description: str | None = None,
    top_k: int = 10,
    max_iterations: int = 3,
    validation_threshold: float = 72,
) -> Iterator[dict[str, Any]]:
    state: SearchWorkflowState = {
        "query": query,
        "job_description": job_description,
        "current_query": query,
        "top_k": top_k,
        "max_iterations": max_iterations,
        "validation_threshold": validation_threshold,
        "best_ranked": [],
        "best_validation": 0.0,
        "validated": False,
        "steps": [],
    }
    state = _search_plan_node(state)
    yield {"type": "step", "step": state["steps"][-1].model_dump(), "parsed_jd": state["parsed_jd"].model_dump()}

    for iteration in range(1, max_iterations + 1):
        state["iteration"] = iteration

        state = _search_retrieve_started_node(state)
        yield {"type": "step", "step": state["steps"][-1].model_dump()}

        state = _search_retrieve_node(state)
        yield {"type": "step_update", "step": state["steps"][-1].model_dump()}

        state = _search_rank_started_node(state)
        yield {"type": "step", "step": state["steps"][-1].model_dump()}

        state = _search_rank_node(state)
        yield {
            "type": "partial_results",
            "step": state["steps"][-1].model_dump(),
            "leaderboard": [candidate.model_dump() for candidate in state["ranked"][:top_k]],
        }

        state = _search_validate_node(state)
        yield {
            "type": "validation",
            "step": state["steps"][-1].model_dump(),
            "validation_score": state["best_validation"],
        }

        if state["validated"]:
            break

        state = _search_query_expansion_node(state)
        yield {
            "type": "loop",
            "step": state["steps"][-1].model_dump(),
            "expanded_query": state["current_query"],
        }

    state = _search_finalize_node(state)
    response = LangGraphSearchResponse(
        query=query,
        expanded_query=state["current_query"],
        iterations=state.get("iteration", 0),
        validated=state["validated"],
        validation_score=round(state["best_validation"], 2),
        parsed_jd=state["parsed_jd"],
        steps=state["steps"],
        leaderboard=state["best_ranked"][:top_k],
    )
    yield {"type": "final", "step": state["steps"][-1].model_dump(), "result": response.model_dump()}


def run_search_workflow(
    query: str,
    job_description: str | None = None,
    top_k: int = 10,
    max_iterations: int = 3,
    validation_threshold: float = 72,
) -> LangGraphSearchResponse:
    result: LangGraphSearchResponse | None = None
    for event in stream_search_workflow(query, job_description, top_k, max_iterations, validation_threshold):
        if event["type"] == "final":
            result = LangGraphSearchResponse(**event["result"])
    if result is None:
        raise RuntimeError("LangGraph search workflow did not produce a final result.")
    return result


def check_jd_resume(
    job_description: str,
    resume_text: str,
    resume_name: str,
    resume_skills: list[str],
    experience: int | None,
) -> JDResumeCheckResponse:
    steps = [
        WorkflowStep(
            step="parse_jd",
            status="complete",
            message="Parsed the job description into skills, experience level, and domain keywords.",
        )
    ]
    parsed_jd = parse_jd(job_description)
    skills = resume_skills or _extract_skills(resume_text)
    candidate_resume = Resume(
        id="manual-check",
        name=resume_name or "Candidate",
        skills=skills,
        experience=experience if experience is not None else _extract_experience(resume_text),
        education=_extract_education(resume_text),
        raw_text=resume_text,
    )
    steps.append(
        WorkflowStep(
            step="parse_resume",
            status="complete",
            message="Extracted resume signals for local scoring.",
            details={"skills": skills, "experience": candidate_resume.experience},
        )
    )
    embeddings = get_embedding_service().encode([job_description, resume_text])
    semantic_similarity = float(np.dot(embeddings[0], embeddings[1]))
    candidate = score_candidate(candidate_resume, None, parsed_jd, semantic_similarity)
    validated = candidate.score >= 72
    steps.append(
        WorkflowStep(
            step="score_and_validate",
            status="complete" if validated else "review",
            message=(
                "Resume is a strong match for this JD."
                if validated
                else "Resume needs recruiter review because important JD signals are weak or missing."
            ),
            details={"score": candidate.score, "semantic_similarity": candidate.semantic_similarity},
        )
    )
    return JDResumeCheckResponse(
        parsed_jd=parsed_jd,
        candidate=candidate,
        validated=validated,
        validation_score=candidate.score,
        steps=steps,
    )


def _load_jd(state: ATSState) -> ATSState:
    job = get_job(state["job_id"]) if state.get("job_id") else None
    description = state.get("job_description") or (job.description if job else "")
    if not description:
        raise ValueError("A job_id or job_description is required.")
    return {**state, "job": job, "job_description": description}


def _parse_jd_node(state: ATSState) -> ATSState:
    explicit = state["job"].required_skills if state.get("job") else None
    parsed = parse_jd(state["job_description"] or "", explicit)
    return {**state, "parsed_jd": parsed}


def _load_resumes_node(state: ATSState) -> ATSState:
    resumes = load_resumes()
    selected = set(state.get("resume_ids") or [])
    if selected:
        resumes = [resume for resume in resumes if resume.id in selected]
    return {**state, "resumes": resumes}


def _generate_embeddings_node(state: ATSState) -> ATSState:
    service = get_search_service()
    service.rebuild(state["resumes"])
    return state


def _semantic_retrieval_node(state: ATSState) -> ATSState:
    similarities = get_search_service().similarities_for_job(state["job_description"] or "", state["resumes"])
    return {**state, "similarities": similarities}


def _score_candidates_node(state: ATSState) -> ATSState:
    candidates = [
        score_candidate(
            resume=resume,
            job=state.get("job"),
            parsed_jd=state["parsed_jd"],
            semantic_similarity=state["similarities"].get(resume.id, 0.0),
        )
        for resume in state["resumes"]
    ]
    return {**state, "candidates": candidates}


def _ranking_node(state: ATSState) -> ATSState:
    return {**state, "leaderboard": rank_candidates(state["candidates"])}


def _report_node(state: ATSState) -> ATSState:
    top = state["leaderboard"][: state.get("top_k", 25)]
    report = {
        "jd_parsed_output": state["parsed_jd"].model_dump(),
        "embedding_similarity_score": {
            candidate.resume_id: candidate.semantic_similarity for candidate in top
        },
        "skill_match_score": {
            candidate.resume_id: candidate.skill_match_ratio for candidate in top
        },
        "final_score_breakdown": {
            candidate.resume_id: candidate.reason_breakdown.model_dump() for candidate in top
        },
        "ranking_decision": [
            {
                "rank": index + 1,
                "resume_id": candidate.resume_id,
                "name": candidate.name,
                "score": candidate.score,
                "why": candidate.explanation,
            }
            for index, candidate in enumerate(top)
        ],
    }
    return {**state, "report": report}


def _ats_completed_message(node_name: str, state: ATSState) -> str:
    messages = {
        "load_jd": "Loaded the job description for ATS scoring.",
        "parse_jd": "Parsed the JD into recruiter-visible structured requirements.",
        "load_resumes": f"Loaded {len(state.get('resumes', []))} resumes for this run.",
        "generate_embeddings": "MiniLM embeddings and FAISS index are ready.",
        "semantic_retrieval": "Semantic similarity scores were calculated for the resume batch.",
        "ats_scoring": f"Calculated ATS scores for {len(state.get('candidates', []))} candidates.",
        "ranking_engine": "Candidate leaderboard has been ranked.",
        "generate_report": "Explanation report and score breakdown are complete.",
    }
    return messages.get(node_name, "Workflow step completed.")


def _ats_step_details(node_name: str, state: ATSState) -> dict[str, Any]:
    if node_name == "parse_jd":
        return state["parsed_jd"].model_dump()
    if node_name == "load_resumes":
        return {"resume_count": len(state.get("resumes", []))}
    if node_name == "semantic_retrieval":
        similarities = state.get("similarities", {})
        return {"scored_resumes": len(similarities)}
    if node_name == "ats_scoring":
        return {"candidate_count": len(state.get("candidates", []))}
    if node_name == "ranking_engine":
        leaderboard = state.get("leaderboard", [])
        return {
            "top_candidate": leaderboard[0].name if leaderboard else None,
            "top_score": leaderboard[0].score if leaderboard else 0,
        }
    return {}


def _search_plan_node(state: SearchWorkflowState) -> SearchWorkflowState:
    parsed = parse_jd(state.get("job_description") or state["query"])
    step = WorkflowStep(
        step="langgraph_plan",
        status="complete",
        message="LangGraph search workflow initialized: parse JD, retrieve candidates, rank, validate, and loop if quality is weak.",
        details={"query": state["query"], "required_skills": parsed.required_skills},
    )
    return {**state, "parsed_jd": parsed, "steps": [*state["steps"], step]}


def _search_retrieve_started_node(state: SearchWorkflowState) -> SearchWorkflowState:
    retrieval_k = max(state["top_k"] * 3, 20)
    step = WorkflowStep(
        step=f"iteration_{state['iteration']}_retrieve",
        status="running",
        message=f"Retrieving resumes with MiniLM embeddings and FAISS for search loop {state['iteration']}.",
        details={"query": state["current_query"], "retrieval_k": retrieval_k},
    )
    return {**state, "steps": [*state["steps"], step]}


def _search_retrieve_node(state: SearchWorkflowState) -> SearchWorkflowState:
    retrieval_k = max(state["top_k"] * 3, 20)
    retrieved = get_search_service().search(state["current_query"], retrieval_k)
    steps = [*state["steps"]]
    steps[-1].status = "complete"
    steps[-1].details["retrieved"] = len(retrieved)
    return {**state, "retrieved": retrieved, "steps": steps}


def _search_rank_started_node(state: SearchWorkflowState) -> SearchWorkflowState:
    step = WorkflowStep(
        step=f"iteration_{state['iteration']}_rank",
        status="running",
        message="Ranking retrieved resumes with ATS score, semantic similarity, skill overlap, and experience match.",
        details={"candidate_count": len(state["retrieved"])},
    )
    return {**state, "steps": [*state["steps"], step]}


def _search_rank_node(state: SearchWorkflowState) -> SearchWorkflowState:
    ranked = rank_candidates(
        [
            score_candidate(result.resume, None, state["parsed_jd"], result.similarity)
            for result in state["retrieved"]
        ]
    )
    steps = [*state["steps"]]
    steps[-1].status = "complete"
    steps[-1].details["top_candidate"] = ranked[0].name if ranked else None
    steps[-1].details["top_score"] = ranked[0].score if ranked else 0
    return {**state, "ranked": ranked, "steps": steps}


def _search_validate_node(state: SearchWorkflowState) -> SearchWorkflowState:
    validation = _validate_search_results(state["ranked"], state["parsed_jd"])
    best_validation = state["best_validation"]
    best_ranked = state["best_ranked"]
    if validation > best_validation:
        best_validation = validation
        best_ranked = state["ranked"]
    validated = validation >= state["validation_threshold"]
    step = WorkflowStep(
        step=f"iteration_{state['iteration']}_validate",
        status="complete" if validated else "retry",
        message=(
            "Validation passed, so LangGraph can finalize the ranking."
            if validated
            else "Validation is below threshold, so LangGraph will expand the query and continue the loop."
        ),
        details={"validation_score": validation, "threshold": state["validation_threshold"]},
    )
    return {
        **state,
        "best_validation": best_validation,
        "best_ranked": best_ranked,
        "validated": validated,
        "steps": [*state["steps"], step],
    }


def _search_query_expansion_node(state: SearchWorkflowState) -> SearchWorkflowState:
    current_query = _expand_search_query(state["current_query"], state["parsed_jd"], state["ranked"])
    step = WorkflowStep(
        step=f"iteration_{state['iteration']}_query_expansion",
        status="complete",
        message="LangGraph expanded the query using missing skill signals and JD keywords before the next retrieval loop.",
        details={"expanded_query": current_query},
    )
    return {**state, "current_query": current_query, "steps": [*state["steps"], step]}


def _search_finalize_node(state: SearchWorkflowState) -> SearchWorkflowState:
    step = WorkflowStep(
        step="finalize",
        status="complete",
        message="LangGraph completed the search workflow and returned the best ranking for recruiter review.",
        details={"validated": state["validated"], "validation_score": round(state["best_validation"], 2)},
    )
    return {**state, "steps": [*state["steps"], step]}


def _validate_search_results(candidates: list[CandidateScore], parsed_jd: ParsedJD) -> float:
    if not candidates:
        return 0.0
    top = candidates[:5]
    avg_score = sum(candidate.score for candidate in top) / len(top)
    required = set(skill.lower() for skill in parsed_jd.required_skills)
    covered = {
        skill.lower()
        for candidate in top
        for skill in candidate.matching_skills
    }
    coverage = len(required & covered) / max(len(required), 1)
    return round((avg_score * 0.75) + (coverage * 25), 2)


def _expand_search_query(query: str, parsed_jd: ParsedJD, candidates: list[CandidateScore]) -> str:
    missing: list[str] = []
    for candidate in candidates[:5]:
        missing.extend(candidate.missing_skills)
    expansion_terms = [*parsed_jd.required_skills, *parsed_jd.domain_keywords, *missing[:4]]
    combined = [query, *_ordered_unique(expansion_terms)]
    return " ".join(term for term in combined if term)


def _ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _extract_skills(text: str) -> list[str]:
    lower = text.lower()
    return sorted({label for needle, label in SKILL_ALIASES.items() if needle in lower})


def _extract_experience(text: str) -> int:
    matches = re.findall(r"(\d+)\+?\s*(?:years|yrs|yr)", text.lower())
    return max([int(match) for match in matches], default=2)


def _extract_education(text: str) -> str:
    lower = text.lower()
    if "phd" in lower or "doctorate" in lower:
        return "PhD"
    if "master" in lower:
        return "Master's"
    if "bachelor" in lower:
        return "Bachelor's"
    return "Not specified"


@lru_cache(maxsize=1)
def get_compiled_ats_graph():
    try:
        from langgraph.graph import END, START, StateGraph

        graph = StateGraph(ATSState)
        graph.add_node("load_jd", _load_jd)
        graph.add_node("parse_jd", _parse_jd_node)
        graph.add_node("load_resumes", _load_resumes_node)
        graph.add_node("generate_embeddings", _generate_embeddings_node)
        graph.add_node("semantic_retrieval", _semantic_retrieval_node)
        graph.add_node("ats_scoring", _score_candidates_node)
        graph.add_node("ranking_engine", _ranking_node)
        graph.add_node("generate_report", _report_node)
        graph.add_edge(START, "load_jd")
        graph.add_edge("load_jd", "parse_jd")
        graph.add_edge("parse_jd", "load_resumes")
        graph.add_edge("load_resumes", "generate_embeddings")
        graph.add_edge("generate_embeddings", "semantic_retrieval")
        graph.add_edge("semantic_retrieval", "ats_scoring")
        graph.add_edge("ats_scoring", "ranking_engine")
        graph.add_edge("ranking_engine", "generate_report")
        graph.add_edge("generate_report", END)
        return graph.compile()
    except Exception as exc:  # pragma: no cover - fallback for explicit test/degraded mode
        if os.getenv("ATS_ALLOW_LANGGRAPH_FALLBACK") != "1":
            raise RuntimeError(
                f"LangGraph workflow is required but could not be compiled: {exc}. "
                "Install backend requirements, then rerun the server. For tests only, set "
                "ATS_ALLOW_LANGGRAPH_FALLBACK=1."
            ) from exc
        return SequentialGraph()


class SequentialGraph:
    def invoke(self, state: ATSState) -> ATSState:
        for node in (
            _load_jd,
            _parse_jd_node,
            _load_resumes_node,
            _generate_embeddings_node,
            _semantic_retrieval_node,
            _score_candidates_node,
            _ranking_node,
            _report_node,
        ):
            state = node(state)
        return state

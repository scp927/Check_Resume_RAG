import os

os.environ.setdefault("ATS_ALLOW_EMBEDDING_FALLBACK", "1")
os.environ.setdefault("ATS_ALLOW_LANGGRAPH_FALLBACK", "1")

from app.models import JobDescription, Resume
from app.services.ats_engine import score_candidate
from app.services.jd_parser import parse_jd
from app.services.langgraph_workflow import check_jd_resume, run_ats_workflow, run_search_workflow
from app.services.search_service import get_search_service
from app.services.storage import load_jobs, load_resumes


def test_parse_jd_extracts_skills_and_experience():
    parsed = parse_jd("Senior React developer with AWS, Kafka, and 6+ years of experience.")
    assert "React" in parsed.required_skills
    assert "AWS" in parsed.required_skills
    assert parsed.min_experience == 6


def test_score_candidate_returns_explanation():
    resume = Resume(
        id="r1",
        name="Test Candidate",
        skills=["React", "AWS", "TypeScript"],
        experience=6,
        education="Bachelor's",
        raw_text="React TypeScript AWS SaaS frontend engineer with 6 years.",
    )
    job = JobDescription(
        id="j1",
        title="Frontend",
        description="React TypeScript AWS role requiring 4 years.",
        required_skills=["React", "TypeScript", "AWS"],
    )
    parsed = parse_jd(job.description, job.required_skills)
    result = score_candidate(resume, job, parsed, 0.82)
    assert result.score > 80
    assert result.explanation
    assert not result.missing_skills


def test_search_service_returns_results():
    resumes = load_resumes()[:25]
    service = get_search_service()
    service.rebuild(resumes)
    results = service.search("React developer with AWS", 5)
    assert len(results) == 5


def test_langgraph_workflow_runs_with_mock_data():
    job = load_jobs()[0]
    result = run_ats_workflow(job_id=job.id, top_k=5)
    assert result.leaderboard
    assert result.process_visibility["ranking_decision"]


def test_langgraph_search_returns_steps_and_rankings():
    result = run_search_workflow(
        query="React developer with AWS",
        job_description="React TypeScript AWS role requiring 4+ years.",
        top_k=5,
        max_iterations=2,
    )
    assert result.steps
    assert result.leaderboard
    assert result.iterations >= 1


def test_jd_resume_checker_scores_manual_candidate():
    result = check_jd_resume(
        job_description="React TypeScript AWS role requiring 4+ years.",
        resume_text="Candidate has 6 years of React, TypeScript, AWS and SaaS experience.",
        resume_name="Manual Candidate",
        resume_skills=[],
        experience=None,
    )
    assert result.candidate.score > 70
    assert result.steps

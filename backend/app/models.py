from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    title: str
    company: str
    location: str
    period: str
    highlights: list[str] = Field(default_factory=list)


class ContactInfo(BaseModel):
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None


class Project(BaseModel):
    name: str
    description: str
    technologies: list[str] = Field(default_factory=list)


class Resume(BaseModel):
    id: str
    name: str
    skills: list[str]
    experience: int
    education: str
    raw_text: str
    summary: str = ""
    work_exp: list[WorkExperience] = Field(default_factory=list)
    work_experience: list[WorkExperience] = Field(default_factory=list)
    certification: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    contact_info: ContactInfo | None = None
    projects: list[Project] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


class JobPoster(BaseModel):
    name: str
    degree: str
    headline: str
    subheadline: str
    label: str


class JobDescription(BaseModel):
    id: str
    title: str
    description: str
    required_skills: list[str]
    poster: JobPoster | None = None


class ParsedJD(BaseModel):
    required_skills: list[str]
    nice_to_have_skills: list[str] = Field(default_factory=list)
    experience_level: str
    min_experience: int
    domain_keywords: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    semantic: float
    skills: float
    experience: float
    keyword_bonus: float


class CandidateScore(BaseModel):
    resume_id: str
    name: str
    score: float
    semantic_similarity: float
    skill_match_ratio: float
    matching_skills: list[str]
    missing_skills: list[str]
    explanation: str
    strengths: list[str]
    weaknesses: list[str]
    reason_breakdown: ScoreBreakdown
    resume: Resume | None = None


class ATSRunRequest(BaseModel):
    job_id: str | None = None
    job_description: str | None = None
    resume_ids: list[str] | None = None
    top_k: int = 25


class ATSRunResponse(BaseModel):
    job: JobDescription | None
    parsed_jd: ParsedJD
    candidate_count: int
    leaderboard: list[CandidateScore]
    process_visibility: dict[str, Any]


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10


class SearchResult(BaseModel):
    resume: Resume
    similarity: float


class WorkflowStep(BaseModel):
    step: str
    status: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class LangGraphSearchRequest(BaseModel):
    query: str
    job_description: str | None = None
    top_k: int = 10
    max_iterations: int = 3
    validation_threshold: float = 72


class LangGraphSearchResponse(BaseModel):
    query: str
    expanded_query: str
    iterations: int
    validated: bool
    validation_score: float
    parsed_jd: ParsedJD
    steps: list[WorkflowStep]
    leaderboard: list[CandidateScore]


class JDResumeCheckRequest(BaseModel):
    job_description: str
    resume_text: str
    resume_name: str = "Candidate"
    resume_skills: list[str] = Field(default_factory=list)
    experience: int | None = None


class JDResumeCheckResponse(BaseModel):
    parsed_jd: ParsedJD
    candidate: CandidateScore
    validated: bool
    validation_score: float
    steps: list[WorkflowStep]


class UploadStatus(BaseModel):
    batch_id: str
    status: str
    total: int
    processed: int
    message: str

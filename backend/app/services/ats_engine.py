from __future__ import annotations

import re

from app.models import CandidateScore, JobDescription, ParsedJD, Resume, ScoreBreakdown


def score_candidate(
    resume: Resume,
    job: JobDescription | None,
    parsed_jd: ParsedJD,
    semantic_similarity: float,
) -> CandidateScore:
    resume_skills = {skill.lower(): skill for skill in resume.skills}
    required_skills = parsed_jd.required_skills or (job.required_skills if job else [])
    matching = [
        skill
        for skill in required_skills
        if skill.lower() in resume_skills or skill.lower() in resume.raw_text.lower()
    ]
    missing = [skill for skill in required_skills if skill not in matching]

    skill_score = len(matching) / max(len(required_skills), 1)
    experience_score = min(resume.experience / max(parsed_jd.min_experience, 1), 1.0)
    keyword_bonus = _keyword_bonus(resume.raw_text, parsed_jd.domain_keywords)
    semantic_score = max(0.0, min((semantic_similarity + 1) / 2, 1.0))

    final = (
        semantic_score * 40
        + skill_score * 35
        + experience_score * 20
        + keyword_bonus * 5
    )
    final_score = round(min(final, 100), 2)

    strengths = _strengths(matching, resume.experience, parsed_jd.min_experience, semantic_score)
    weaknesses = _weaknesses(missing, resume.experience, parsed_jd.min_experience)

    return CandidateScore(
        resume_id=resume.id,
        name=resume.name,
        score=final_score,
        semantic_similarity=round(float(semantic_similarity), 4),
        skill_match_ratio=round(skill_score, 4),
        matching_skills=matching,
        missing_skills=missing,
        explanation=_explain(resume, matching, missing, parsed_jd, semantic_score, final_score),
        strengths=strengths,
        weaknesses=weaknesses,
        reason_breakdown=ScoreBreakdown(
            semantic=round(semantic_score * 40, 2),
            skills=round(skill_score * 35, 2),
            experience=round(experience_score * 20, 2),
            keyword_bonus=round(keyword_bonus * 5, 2),
        ),
        resume=resume,
    )


def rank_candidates(candidates: list[CandidateScore]) -> list[CandidateScore]:
    return sorted(
        candidates,
        key=lambda item: (item.score, item.semantic_similarity, item.skill_match_ratio),
        reverse=True,
    )


def _keyword_bonus(text: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    lower = text.lower()
    hits = sum(1 for keyword in keywords if re.search(rf"\b{re.escape(keyword.lower())}\b", lower))
    return min(hits / len(keywords), 1.0)


def _strengths(
    matching: list[str],
    experience: int,
    required_experience: int,
    semantic_score: float,
) -> list[str]:
    strengths: list[str] = []
    if matching:
        strengths.append(f"Matches {len(matching)} required skills: {', '.join(matching[:6])}.")
    if experience >= required_experience:
        strengths.append(f"Meets the experience target with {experience} years.")
    if semantic_score >= 0.75:
        strengths.append("Resume language is strongly aligned with the job description.")
    return strengths or ["Has partial alignment with the role requirements."]


def _weaknesses(missing: list[str], experience: int, required_experience: int) -> list[str]:
    weaknesses: list[str] = []
    if missing:
        weaknesses.append(f"Missing or unclear required skills: {', '.join(missing[:6])}.")
    if experience < required_experience:
        weaknesses.append(f"Experience is below the requested {required_experience}+ years.")
    return weaknesses or ["No major gaps detected from the available resume text."]


def _explain(
    resume: Resume,
    matching: list[str],
    missing: list[str],
    parsed_jd: ParsedJD,
    semantic_score: float,
    final_score: float,
) -> str:
    match_text = ", ".join(matching[:5]) if matching else "some adjacent experience"
    gap_text = f" However, {', '.join(missing[:4])} are not clearly represented." if missing else ""
    semantic_text = "strong" if semantic_score >= 0.75 else "moderate" if semantic_score >= 0.55 else "limited"
    return (
        f"{resume.name} scores {final_score} because their resume shows {semantic_text} semantic alignment "
        f"with the JD and matches {match_text}. They have {resume.experience} years against a "
        f"{parsed_jd.min_experience}+ year target.{gap_text}"
    )

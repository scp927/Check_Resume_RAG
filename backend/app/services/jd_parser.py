from __future__ import annotations

import re

from app.models import ParsedJD


SKILL_ALIASES = {
    "react": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "python": "Python",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "java": "Java",
    "spring": "Spring",
    "node": "Node.js",
    "node.js": "Node.js",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "kafka": "Kafka",
    "spark": "Spark",
    "airflow": "Airflow",
    "sql": "SQL",
    "graphql": "GraphQL",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "nlp": "NLP",
    "llm": "LLM",
    "security": "Security",
    "soc2": "SOC2",
    "ci/cd": "CI/CD",
    "github actions": "GitHub Actions",
    "tailwind": "TailwindCSS",
}

DOMAIN_KEYWORDS = [
    "fintech",
    "healthcare",
    "ecommerce",
    "saas",
    "security",
    "analytics",
    "platform",
    "infrastructure",
    "mobile",
    "recruiting",
]


def parse_jd(description: str, explicit_required: list[str] | None = None) -> ParsedJD:
    text = description or ""
    lower = text.lower()
    found = _extract_skills(lower)
    required = _ordered_unique([*(explicit_required or []), *found])
    nice_to_have = _extract_nice_to_have(text, required)
    min_experience = _extract_experience(lower)
    domains = [keyword for keyword in DOMAIN_KEYWORDS if keyword in lower]

    return ParsedJD(
        required_skills=required,
        nice_to_have_skills=nice_to_have,
        experience_level=_experience_label(min_experience),
        min_experience=min_experience,
        domain_keywords=domains,
    )


def _extract_skills(lower_text: str) -> list[str]:
    skills: list[str] = []
    for needle, label in SKILL_ALIASES.items():
        pattern = r"(?<![a-z0-9+#])" + re.escape(needle) + r"(?![a-z0-9+#])"
        if re.search(pattern, lower_text):
            skills.append(label)
    return _ordered_unique(skills)


def _extract_nice_to_have(text: str, required: list[str]) -> list[str]:
    lower = text.lower()
    optional_sections = re.findall(
        r"(?:nice to have|preferred|bonus|plus)[:\-\s]+([^.\n]+)",
        lower,
        flags=re.IGNORECASE,
    )
    optional_text = " ".join(optional_sections)
    skills = _extract_skills(optional_text)
    return [skill for skill in skills if skill not in required]


def _extract_experience(lower_text: str) -> int:
    matches = re.findall(r"(\d+)\+?\s*(?:years|yrs|yr)", lower_text)
    if matches:
        return max(int(match) for match in matches)
    if "senior" in lower_text or "staff" in lower_text or "lead" in lower_text:
        return 5
    if "mid" in lower_text:
        return 3
    if "junior" in lower_text or "entry" in lower_text:
        return 1
    return 2


def _experience_label(years: int) -> str:
    if years >= 7:
        return "senior"
    if years >= 4:
        return "mid-senior"
    if years >= 2:
        return "mid-level"
    return "junior"


def _ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.strip()
        if normalized and normalized.lower() not in seen:
            seen.add(normalized.lower())
            result.append(normalized)
    return result

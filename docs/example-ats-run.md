# Example ATS Run Output

Input JD: `Senior Frontend Engineer`

## Parsed JD

```json
{
  "required_skills": ["React", "Next.js", "TypeScript", "AWS"],
  "nice_to_have_skills": ["analytics", "security"],
  "experience_level": "mid-senior",
  "min_experience": 4,
  "domain_keywords": ["saas"]
}
```

## Leaderboard

1. Candidate A - 92.4
2. Candidate B - 88.1
3. Candidate C - 85.7

## Candidate Explanation

Candidate A ranks high because their resume strongly aligns semantically with the job description, directly matches React, Next.js, TypeScript, and AWS, and exceeds the requested 4+ years of experience. They are ranked above Candidate B because Candidate B has similar frontend skills but weaker AWS evidence and a lower semantic similarity score.

## Score Breakdown

```json
{
  "semantic": 36.2,
  "skills": 35.0,
  "experience": 20.0,
  "keyword_bonus": 1.2,
  "final_score": 92.4
}
```

The report is intentionally structured and concise. It explains recruiter-visible factors without exposing hidden chain-of-thought.

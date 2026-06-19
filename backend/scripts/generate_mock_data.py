from __future__ import annotations

import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

PEOPLE = [
    ("Amara", "Okafor", "Lagos, Nigeria"),
    ("Mateo", "Alvarez", "Madrid, Spain"),
    ("Sofia", "Rossi", "Milan, Italy"),
    ("Hiro", "Tanaka", "Tokyo, Japan"),
    ("Priya", "Nair", "Bengaluru, India"),
    ("Lucas", "Meyer", "Berlin, Germany"),
    ("Camille", "Moreau", "Paris, France"),
    ("Noah", "Wilson", "Toronto, Canada"),
    ("Lina", "Andersson", "Stockholm, Sweden"),
    ("Diego", "Santos", "Sao Paulo, Brazil"),
    ("Aisha", "Khan", "Dubai, UAE"),
    ("Mina", "Park", "Seoul, South Korea"),
    ("Ethan", "Brooks", "Austin, USA"),
    ("Isabella", "Martinez", "Mexico City, Mexico"),
    ("Oliver", "Taylor", "London, UK"),
    ("Mei", "Zhang", "Singapore"),
    ("Nadia", "Hassan", "Cairo, Egypt"),
    ("Tomas", "Novak", "Prague, Czech Republic"),
    ("Anika", "Schmidt", "Zurich, Switzerland"),
    ("Liam", "O'Connor", "Dublin, Ireland"),
]

ROLE_PROFILES = {
    "Senior Frontend Engineer": {
        "skills": ["React", "Next.js", "TypeScript", "JavaScript", "GraphQL", "TailwindCSS", "Testing", "AWS"],
        "domains": ["B2B SaaS", "marketplaces", "consumer platforms", "healthcare portals"],
        "impact": ["cut page load time by 38%", "raised design-system adoption across 14 product teams", "improved conversion on onboarding by 11%"],
    },
    "Backend Platform Engineer": {
        "skills": ["Python", "FastAPI", "Kafka", "PostgreSQL", "Redis", "Docker", "Kubernetes", "AWS"],
        "domains": ["payments", "logistics", "identity", "developer platforms"],
        "impact": ["processed 120M events per month", "reduced API latency by 42%", "migrated monolith services into resilient microservices"],
    },
    "Machine Learning Engineer": {
        "skills": ["Python", "Machine Learning", "PyTorch", "TensorFlow", "NLP", "LLM", "FastAPI", "Docker"],
        "domains": ["search relevance", "document intelligence", "personalization", "risk scoring"],
        "impact": ["improved ranking precision by 18%", "deployed online inference under 140ms p95", "built offline evaluation pipelines"],
    },
    "Data Engineer": {
        "skills": ["Python", "SQL", "Spark", "Airflow", "Kafka", "PostgreSQL", "dbt", "AWS"],
        "domains": ["finance analytics", "customer data platforms", "growth intelligence", "supply chain"],
        "impact": ["reduced reporting delay from 24 hours to 20 minutes", "improved data quality checks across 180 tables", "built governed metric layers"],
    },
    "Security Platform Engineer": {
        "skills": ["Security", "SOC2", "Python", "AWS", "Kubernetes", "Terraform", "SIEM", "Zero Trust"],
        "domains": ["cloud security", "compliance automation", "identity systems", "incident response"],
        "impact": ["automated 70% of compliance evidence collection", "reduced critical alert noise by 45%", "hardened multi-account AWS environments"],
    },
    "DevOps Engineer": {
        "skills": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "GitHub Actions", "Linux", "Prometheus"],
        "domains": ["platform reliability", "cloud migrations", "observability", "release engineering"],
        "impact": ["improved deployment frequency from weekly to daily", "cut infrastructure drift incidents by 60%", "built golden-path CI/CD templates"],
    },
    "Mobile Engineer": {
        "skills": ["React Native", "TypeScript", "JavaScript", "GraphQL", "Testing", "CI/CD", "UX", "AWS"],
        "domains": ["fintech apps", "telehealth", "retail mobile", "field operations"],
        "impact": ["raised crash-free sessions to 99.8%", "reduced release cycle time by 35%", "rebuilt offline workflows for global users"],
    },
    "Analytics Engineer": {
        "skills": ["SQL", "Python", "dbt", "Airflow", "Tableau", "Analytics", "Snowflake", "SaaS"],
        "domains": ["revenue analytics", "product analytics", "growth experimentation", "executive reporting"],
        "impact": ["standardized ARR reporting across regions", "launched self-serve dashboards for 300 users", "improved experiment readouts"],
    },
}

JOB_SPECS = [
    ("Senior Full-Stack Engineer", ["React", "Next.js", "TypeScript", "AWS"], "USA | Remote", "$150K - $250K | 0.5% - 1.5% Equity", "AI-native enterprise workflow application"),
    ("Senior Frontend Engineer, Growth Platform", ["React", "Next.js", "TypeScript", "GraphQL"], "Canada | Remote", "$140K - $220K | 0.3% - 1.0% Equity", "global B2B SaaS onboarding"),
    ("Backend Platform Engineer, Payments", ["Python", "FastAPI", "Kafka", "PostgreSQL"], "UK | Hybrid London", "GBP 105K - GBP 165K | Equity", "real-time international payments"),
    ("Machine Learning Engineer, Search Relevance", ["Python", "Machine Learning", "PyTorch", "NLP"], "Germany | Remote EU", "EUR 100K - EUR 170K | Equity", "semantic product and document search"),
    ("Data Engineer, Customer Intelligence", ["Python", "Spark", "Airflow", "Kafka"], "Singapore | Hybrid", "SGD 150K - SGD 230K | Equity", "multi-region customer analytics"),
    ("Security Platform Engineer", ["Security", "SOC2", "AWS", "Python"], "USA | Remote", "$160K - $240K | Equity", "cloud security and compliance automation"),
    ("DevOps Engineer, Global Infrastructure", ["AWS", "Kubernetes", "Terraform", "Docker"], "Netherlands | Remote EU", "EUR 95K - EUR 155K | Equity", "multi-cloud platform operations"),
    ("Mobile Engineer, Consumer Finance", ["React Native", "TypeScript", "GraphQL", "CI/CD"], "Brazil | Remote LATAM", "$90K - $160K | Equity", "international mobile banking"),
    ("Analytics Engineer, Revenue Operations", ["SQL", "dbt", "Python", "Airflow"], "Ireland | Hybrid Dublin", "EUR 85K - EUR 140K | Equity", "global go-to-market analytics"),
    ("Full Stack Engineer, Healthcare SaaS", ["React", "Node.js", "PostgreSQL", "TypeScript"], "Australia | Remote", "AUD 150K - AUD 220K | Equity", "care coordination workflows"),
    ("AI Product Engineer, Workflow Automation", ["LLM", "NLP", "Python", "React"], "USA | Remote", "$155K - $245K | 0.4% - 1.2% Equity", "enterprise automation assistants"),
    ("Senior Java Engineer, Trading Systems", ["Java", "Spring", "Kafka", "AWS"], "Switzerland | Hybrid Zurich", "CHF 145K - CHF 230K | Bonus", "low-latency financial platforms"),
    ("Cloud Data Architect", ["AWS", "Spark", "Airflow", "Terraform"], "India | Hybrid Bengaluru", "INR 55L - INR 90L | Equity", "regional data platform modernization"),
    ("Reliability Engineer, Kubernetes Platform", ["Kubernetes", "Docker", "Terraform", "CI/CD"], "Japan | Hybrid Tokyo", "JPY 14M - JPY 24M | Equity", "high-availability SaaS infrastructure"),
    ("Fintech Backend Engineer", ["Python", "FastAPI", "PostgreSQL", "Kafka"], "UAE | Hybrid Dubai", "AED 420K - AED 680K | Equity", "risk, ledger, and account APIs"),
    ("Frontend Engineer, Accessibility Systems", ["React", "TypeScript", "GraphQL", "AWS"], "France | Remote EU", "EUR 85K - EUR 145K | Equity", "regulated healthcare portals"),
    ("MLOps Engineer", ["Python", "Docker", "Kubernetes", "PyTorch"], "South Korea | Hybrid Seoul", "KRW 110M - KRW 180M | Equity", "model serving and monitoring"),
    ("Security Automation Engineer", ["Terraform", "AWS", "Kubernetes", "Security"], "Sweden | Remote EU", "SEK 950K - SEK 1.5M | Equity", "policy as code and detection engineering"),
    ("Ecommerce Full Stack Engineer", ["React", "Node.js", "Redis", "PostgreSQL"], "Mexico | Remote LATAM", "$85K - $150K | Equity", "marketplace catalog and checkout"),
    ("Senior Product Data Analyst", ["SQL", "Python", "Tableau", "Analytics"], "Spain | Hybrid Madrid", "EUR 80K - EUR 130K | Equity", "product-led growth measurement"),
    ("Recruiting AI Engineer", ["NLP", "Python", "FastAPI", "React"], "USA | Remote", "$145K - $230K | Equity", "candidate intelligence and matching systems"),
]

JOB_POSTERS = [
    {
        "name": "Krutika Jhaveri",
        "degree": "3rd",
        "headline": "HR Technology & Talent Acquisition Consultant | Startup & Staffing",
        "subheadline": "Recruitment Specialist | Diversity, Equity & Inclusion Advocate | Ex-Leadership Recruiter at AWS | MBA in IT | Freelance Interview Coach",
        "label": "Job poster",
    },
    {
        "name": "Maya Chen",
        "degree": "2nd",
        "headline": "Technical Recruiting Lead | AI Startups | Global Engineering Hiring",
        "subheadline": "Former SaaS Talent Partner | Engineering Leadership Search | DEI Hiring Programs | Interview Coach",
        "label": "Job poster",
    },
    {
        "name": "Arjun Mehta",
        "degree": "3rd",
        "headline": "Startup Talent Partner | Product Engineering & Infrastructure Recruiting",
        "subheadline": "Ex-Cloud Platform Recruiter | MBA | Remote Team Hiring | Compensation Advisory",
        "label": "Job poster",
    },
]


def main() -> None:
    random.seed(42)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    resumes = [_resume(index) for index in range(1, 1001)]
    jobs = [
        _job(index, title, skills, location, compensation, domain)
        for index, (title, skills, location, compensation, domain) in enumerate(JOB_SPECS, start=1)
    ]
    (DATA_DIR / "resumes.json").write_text(json.dumps(resumes, indent=2), encoding="utf-8")
    (DATA_DIR / "jobs.json").write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    print(f"Generated {len(resumes)} resumes and {len(jobs)} jobs in {DATA_DIR}")


def _resume(index: int) -> dict:
    role = random.choice(list(ROLE_PROFILES))
    profile = ROLE_PROFILES[role]
    first, last, location = random.choice(PEOPLE)
    skills = sorted(set(random.sample(profile["skills"], k=random.randint(5, min(8, len(profile["skills"]))))))
    experience = random.randint(2, 14)
    domain = random.choice(profile["domains"])
    impacts = random.sample(profile["impact"], 2)
    company = random.choice(["Atlassian", "Nubank", "Roche", "Shopify", "Grab", "Wise", "Mercado Libre", "Siemens", "Canva", "Stripe"])
    education = random.choice([
        "B.S. Computer Science, University of Toronto",
        "M.S. Software Engineering, Technical University of Munich",
        "B.Tech Information Technology, National Institute of Technology",
        "M.S. Data Science, University College London",
        "B.S. Information Systems, National University of Singapore",
        "B.Eng. Computer Engineering, University of Sao Paulo",
    ])
    name = f"{first} {last}"
    sanitized_last = last.lower().replace("'", "")
    handle = f"{first.lower()}{sanitized_last}"
    email = f"{first.lower()}.{sanitized_last}@example.com"
    summary = (
        f"{role} based in {location} with {experience} years of experience building {domain} products for international users. "
        f"Strong record of delivering reliable production software, partnering with cross-functional teams, and improving measurable product outcomes."
    )
    work_experience = [
        {
            "title": role,
            "company": company,
            "location": location,
            "period": f"{2025 - min(experience, 6)} - Present",
            "highlights": [
                f"Owned core {domain} features used across multiple regions and collaborated with product, design, data, and security teams.",
                f"Delivered measurable impact: {impacts[0]}.",
                f"Improved system quality through testing, observability, documentation, and architecture reviews.",
            ],
        },
        {
            "title": random.choice(["Software Engineer", "Product Engineer", "Platform Engineer", "Application Engineer"]),
            "company": random.choice(["Airbnb", "Revolut", "Thoughtworks", "Zalando", "Rappi", "Telus", "Booking.com", "Gojek"]),
            "location": random.choice(["Remote", "London, UK", "Singapore", "Toronto, Canada", "Berlin, Germany", "Mexico City, Mexico"]),
            "period": f"{2025 - experience} - {2025 - min(experience, 6)}",
            "highlights": [
                f"Built and maintained customer-facing systems using {', '.join(skills[:4])}.",
                f"Partnered with distributed stakeholders to ship roadmap work and resolve production issues.",
                f"Contributed to engineering standards, code reviews, onboarding docs, and delivery planning.",
            ],
        },
    ]
    certifications = random.sample(
        [
            "AWS Certified Solutions Architect - Associate",
            "Certified Kubernetes Application Developer",
            "Google Professional Cloud Developer",
            "Databricks Lakehouse Fundamentals",
            "Professional Scrum Master I",
            "Meta Front-End Developer Professional Certificate",
            "HashiCorp Terraform Associate",
            "ISC2 Certified in Cybersecurity",
        ],
        k=random.randint(1, 3),
    )
    projects = [
        {
            "name": f"{domain.title()} Operations Console",
            "description": f"Designed an internal dashboard for monitoring workflows, surfacing customer issues, and improving team response time. {impacts[1].capitalize()}.",
            "technologies": skills[:5],
        }
    ]
    languages = random.sample(
        ["English", "Spanish", "French", "German", "Hindi", "Japanese", "Portuguese", "Korean", "Arabic", "Mandarin"],
        k=random.randint(2, 4),
    )
    raw_text = _resume_text(name, skills, education, summary, work_experience, certifications, projects, languages)
    return {
        "id": f"res-{index:04d}",
        "name": name,
        "skills": skills,
        "experience": experience,
        "education": education,
        "raw_text": raw_text,
        "summary": summary,
        "work_exp": work_experience,
        "work_experience": work_experience,
        "certification": certifications,
        "certifications": certifications,
        "contact_info": {
            "email": email,
            "phone": f"+1-555-{index % 9000 + 1000}",
            "location": location,
            "linkedin": f"https://linkedin.com/in/{handle}",
            "github": f"https://github.com/{handle}",
        },
        "projects": projects,
        "languages": languages,
    }


def _resume_text(
    name: str,
    skills: list[str],
    education: str,
    summary: str,
    work_experience: list[dict],
    certifications: list[str],
    projects: list[dict],
    languages: list[str],
) -> str:
    work_lines = []
    for item in work_experience:
        work_lines.append(f"{item['title']} | {item['company']} | {item['location']} | {item['period']}")
        work_lines.extend(f"- {highlight}" for highlight in item["highlights"])
    project_lines = [
        f"{project['name']}: {project['description']} Technologies: {', '.join(project['technologies'])}."
        for project in projects
    ]
    return (
        f"{name}\n\n"
        f"Summary\n{summary}\n\n"
        f"Skills\n{', '.join(skills)}\n\n"
        f"Work Experience\n{chr(10).join(work_lines)}\n\n"
        f"Education\n{education}\n\n"
        f"Certifications\n{chr(10).join(f'- {certification}' for certification in certifications)}\n\n"
        f"Projects\n{chr(10).join(project_lines)}\n\n"
        f"Languages\n{', '.join(languages)}"
    )


def _job(index: int, title: str, skills: list[str], location: str, compensation: str, domain: str) -> dict:
    poster = JOB_POSTERS[(index - 1) % len(JOB_POSTERS)]
    description = (
        f"About the job\n"
        f"Title: {title}\n\n"
        "Target: Masters/Bachelors from top schools such as Stanford, MIT, Carnegie Mellon, Berkeley, Oxford, Cambridge, IIT, NUS, ETH Zurich, or equivalent professional achievement, with a passion for beautiful, user-centric products.\n\n"
        f"Location: {location}\n\n"
        f"Compensation: {compensation}\n\n"
        "Visa Sponsorship: Not Available\n\n\n"
        "About Us\n\n"
        f"We are a pre-launch startup backed by First Round Capital and Y Combinator, building {domain}. "
        "Our product is a complex, interactive web application that feels as simple and intuitive as the best consumer software. "
        "The founding team has previously built and sold a venture-backed company to a major public cloud data platform, and the current team is small, senior, and highly technical.\n\n\n"
        "The Role\n\n"
        f"As a {title} on our engineering team of about 10 people, you will play a key role in building and scaling user-facing features that power how people access, understand, and use AI-enabled workflows. "
        "You will own product surfaces end-to-end, collaborate closely with design and product, make pragmatic architecture decisions, and ship polished experiences that customers can rely on. "
        "We work asynchronously using Slack, Notion, and Linear, prioritizing deep focus, thoughtful writing, and uninterrupted time to build.\n\n"
        "If you are excited about crafting great software, working with cutting-edge AI infrastructure, and contributing to a fast-growing platform before launch, we would love to hear from you.\n\n\n"
        "Ideal Profile\n\n"
        "Experience\n"
        "4+ years of professional full-stack or product engineering experience\n"
        "Proven track record of shipping user-facing products in startup, scale-up, or high-ownership engineering environments\n"
        "Experience building complex web apps, interactive dashboards, internal tools, workflow software, or clean open-source projects\n\n"
        "Technical Strength\n"
        f"Strong experience with {', '.join(skills)}\n"
        "Strong product intuition, modern JavaScript/runtime knowledge, API design fundamentals, and comfort debugging production systems\n"
        "Experience with Cloudflare Workers, serverless platforms, edge-first architectures, AI infrastructure, observability, or design systems is a plus\n\n"
        "Startup Mindset\n"
        "Comfortable in fast-moving, ambiguous environments\n"
        "Proactive, resourceful, and excited to take ownership without waiting for perfect requirements\n"
        "Able to make tradeoffs, communicate decisions clearly, and move from prototype to production with care\n\n"
        "Collaborative & Self-Directed\n"
        "Clear communicator who works well in async teams\n"
        "Able to self-manage and deliver high-quality results independently\n"
        "Comfortable collaborating with founders, designers, customers, and other engineers across time zones\n\n"
        "Craft-Focused Engineer\n"
        "You care deeply about UX, performance, maintainability, accessibility, and small product details\n"
        "You aim to ship delightful, impactful features, not just functional code\n\n\n"
        "Apply if you've built: complex web apps, interactive dashboards, workflow tools, AI products, developer platforms, or have a GitHub profile full of clean, well-documented code."
    )
    return {
        "id": f"job-{index:03d}",
        "title": title,
        "description": description,
        "required_skills": skills,
        "poster": poster,
    }


if __name__ == "__main__":
    main()

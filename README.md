# RecruitAI ATS

RecruitAI ATS is a full-stack AI recruiting platform built as a production-style portfolio project. It combines a Next.js recruiting workspace with a FastAPI AI backend that runs on free, local, open-source tooling: MiniLM embeddings, FAISS semantic search, LangGraph workflow orchestration, deterministic JD parsing, and JSON-based storage.

The app is designed for recruiters and hiring teams who need to browse structured resumes, review detailed job descriptions, run ATS scoring, inspect candidate ranking evidence, and open full candidate/JD detail modals.

## Key Features

- Professional ATS dashboard for pipeline, requisitions, and screening workflow visibility.
- Candidate directory with `1000` realistic worldwide resumes.
- Structured resume data with `summary`, `work_exp`, `education`, `certification`, plus optional `contact_info`, `projects`, and `languages`.
- Detailed global job descriptions with job poster metadata, recruiter avatar blocks, compensation, location, visa status, company context, role expectations, and ideal profile sections.
- Combined `Screening` action that runs ATS scoring and semantic search together.
- Clickable ATS result rows with full candidate detail modal, score breakdown, matched/missing skills, and complete structured resume content.
- JD detail modal with full job description and hiring team/job poster section.
- Batch resume upload for PDF, DOCX, and TXT files.
- Local MiniLM embedding generation using `sentence-transformers/all-MiniLM-L6-v2`.
- FAISS vector search over resume text.
- LangGraph-powered workflow steps for parsing, retrieval, scoring, ranking, validation, and reporting.
- No OpenAI, no paid APIs, no external AI services, and no API keys required.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js 15, React, TypeScript, TailwindCSS |
| Backend | FastAPI, Python, Pydantic |
| AI / ML | sentence-transformers MiniLM, FAISS, LangGraph, PyTorch CPU |
| Parsing | PyPDF, python-docx, deterministic JD/resume parsing |
| Storage | Local JSON files in `data/` |
| Deployment | Local, Docker Compose, or separate frontend/backend hosting |

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI routes
│   │   ├── services/             # ATS engine, search, embeddings, workflow, parsing
│   │   ├── main.py               # FastAPI entrypoint
│   │   └── models.py             # Pydantic models
│   ├── scripts/
│   │   └── generate_mock_data.py # Generates resumes and job descriptions
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                      # Next.js App Router pages
│   ├── components/               # UI and ATS components
│   ├── lib/                      # API client and helpers
│   ├── types/                    # TypeScript domain types
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── resumes.json
│   └── jobs.json
└── docker-compose.yml
```

## Prerequisites

- Windows, macOS, or Linux
- Python 3.11 recommended
- Node.js 20+ recommended
- Docker Desktop, optional
- Git, if publishing to GitHub

## Local Development

Run the backend and frontend in separate terminals.

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/generate_mock_data.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend URL:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/api/health
```

The first real embedding/search request downloads `sentence-transformers/all-MiniLM-L6-v2` into the local HuggingFace cache. This can take a few minutes depending on the machine and network.

### 2. Frontend

```powershell
cd frontend
npm install
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000/api"
npm run dev
```

Frontend URL:

```text
http://localhost:3000/dashboard
```

If your backend is running on another port, update `NEXT_PUBLIC_API_BASE_URL`.

## Docker Deployment

The repository includes a Docker Compose setup for running both services locally.

```powershell
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API health: `http://localhost:8000/api/health`

Stop containers:

```powershell
docker compose down
```

Rebuild after dependency changes:

```powershell
docker compose up --build --force-recreate
```

## Production Deployment Guide

This app can be deployed in two common ways.

### Option A: Single Docker Host

Use this when deploying to a VPS, Docker server, or self-hosted machine.

1. Install Docker and Docker Compose on the server.
2. Clone the repository.
3. Generate or commit the `data/` JSON files.
4. Run:

```bash
docker compose up --build -d
```

5. Put a reverse proxy such as Nginx, Caddy, or Traefik in front of:

```text
frontend:3000
backend:8000
```

6. Configure the frontend environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com/api
```

### Option B: Separate Frontend and Backend Hosting

Recommended split:

- Frontend: Vercel, Netlify, or any Node.js host
- Backend: Render, Railway, Fly.io, a VPS, or Docker host
- Data: keep JSON files mounted/persisted with the backend

Frontend production build:

```powershell
cd frontend
npm install
npm run build
npm run start
```

Backend production start:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_mock_data.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Required frontend environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com/api
```

Backend CORS currently allows local frontend origins. For a real production domain, update `backend/app/main.py`:

```python
allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.com",
]
```

## Environment Variables

| Variable | App | Required | Description |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Yes for deployment | Backend API base URL, for example `https://api.example.com/api` |
| `ATS_ALLOW_EMBEDDING_FALLBACK` | Backend | No | Test-only deterministic embedding fallback |
| `ATS_ALLOW_LANGGRAPH_FALLBACK` | Backend | No | Test-only workflow fallback |

Do not enable fallback variables for production demos if you want MiniLM and LangGraph to run normally.

## Data Generation

Generate the local dataset:

```powershell
cd backend
python scripts/generate_mock_data.py
```

Generated files:

- `data/resumes.json`
- `data/jobs.json`

Current generated dataset:

- `1000` structured resumes
- `21` detailed job descriptions
- Multiple job posters, including Krutika Jhaveri

## API Reference

Base URL:

```text
http://localhost:8000/api
```

Useful endpoints:

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Backend health and model/workflow metadata |
| `GET` | `/resumes?limit=1000` | List resumes |
| `GET` | `/resumes/stats` | Resume corpus stats |
| `GET` | `/jobs` | List job descriptions |
| `POST` | `/jobs/parse` | Parse a JD into structured requirements |
| `POST` | `/search` | Basic semantic resume search |
| `POST` | `/search/langgraph` | LangGraph semantic search workflow |
| `POST` | `/search/langgraph/stream` | Streaming search workflow events |
| `POST` | `/ats/run` | ATS scoring run |
| `POST` | `/ats/run/stream` | Streaming ATS workflow events |
| `POST` | `/ats/check` | Check one JD against one resume |
| `POST` | `/upload/resumes` | Upload PDF/DOCX/TXT resumes |

Example:

```powershell
Invoke-RestMethod http://localhost:8000/api/health

Invoke-RestMethod `
  -Method Post `
  http://localhost:8000/api/ats/run `
  -ContentType "application/json" `
  -Body '{"job_id":"job-001","top_k":10}'
```

## Testing and Quality Checks

Backend tests:

```powershell
cd backend
python -m pytest
```

Frontend typecheck:

```powershell
cd frontend
npm run typecheck
```

Frontend build:

```powershell
cd frontend
npm run build
```

## Git and GitHub Setup

Initialize Git:

```powershell
git init
git add .
git commit -m "Initial commit: AI recruiting ATS platform"
```

Create a GitHub repository, then connect it:

```powershell
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Recommended branch workflow:

```powershell
git checkout -b feature/readme-deployment-docs
git add .
git commit -m "Document deployment and setup workflow"
git push -u origin feature/readme-deployment-docs
```

Then open a pull request on GitHub.

## Deployment Checklist

- Generate fresh data with `python scripts/generate_mock_data.py`.
- Confirm backend health at `/api/health`.
- Confirm frontend has `NEXT_PUBLIC_API_BASE_URL` pointing to the deployed backend.
- Update backend CORS for the deployed frontend domain.
- Persist or mount `data/` for backend deployments.
- Run backend tests with `python -m pytest`.
- Run frontend typecheck with `npm run typecheck`.
- Run frontend build with `npm run build`.
- Commit code to Git and push to GitHub.

## Troubleshooting

### `uvicorn` is not recognized

Use Python module execution:

```powershell
python -m uvicorn app.main:app --reload
```

### Frontend cannot reach backend

Check:

- Backend is running.
- `NEXT_PUBLIC_API_BASE_URL` matches backend port/domain.
- Backend CORS includes the frontend origin.

### First search is slow

The first MiniLM request downloads and loads the local embedding model. Later requests use the local cache.

### Docker frontend points to wrong backend

Update `docker-compose.yml`:

```yaml
environment:
  - NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

For production, use the deployed backend URL instead.

## Notes

This project is intentionally local-first and free-API-first. It is suitable for portfolio demos, technical interviews, and local experimentation with ATS scoring, resume matching, semantic search, and transparent AI workflow design.

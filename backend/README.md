# Backend

FastAPI backend for the local AI Recruiting ATS.

## Services

- `embedding_service.py`: MiniLM embeddings with deterministic local fallback.
- `search_service.py`: FAISS index and semantic resume search.
- `jd_parser.py`: deterministic JD parsing for skills, experience, and domains.
- `ats_engine.py`: score calculation and recruiter-facing explanations.
- `langgraph_workflow.py`: modular ATS pipeline.
- `document_parser.py`: local PDF/DOCX/TXT extraction.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_mock_data.py
uvicorn app.main:app --reload
```

## Test

```powershell
python -m pytest
```

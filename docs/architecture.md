# Architecture

```mermaid
flowchart TD
  recruiter["Recruiter"] --> nextApp["Next.js 15 UI"]
  nextApp --> fastApi["FastAPI API"]
  fastApi --> jsonStore["JSON Storage"]
  fastApi --> upload["Upload Parser"]
  fastApi --> graph["LangGraph ATS Workflow"]
  graph --> jdParser["JD Parser"]
  graph --> embeddings["MiniLM Embeddings"]
  graph --> faiss["FAISS Retrieval"]
  graph --> scorer["ATS Scoring"]
  graph --> ranker["Ranking Engine"]
  ranker --> report["Explanation Report"]
```

The system is local-first. JSON files provide persistence, in-memory state tracks uploads, MiniLM creates embeddings, FAISS provides semantic retrieval, and deterministic scoring generates recruiter-visible explanations without exposing hidden chain-of-thought.

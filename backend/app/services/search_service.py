from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from app.models import Resume, SearchResult
from app.services.embedding_service import EMBEDDING_DIMENSION, get_embedding_service
from app.services.storage import ROOT_DIR, load_resumes

CACHE_DIR = ROOT_DIR / "backend" / ".cache"
EMBEDDINGS_PATH = CACHE_DIR / "resume_embeddings.npy"
METADATA_PATH = CACHE_DIR / "resume_embeddings.json"


class SearchService:
    def __init__(self) -> None:
        self.index = None
        self.resume_ids: list[str] = []
        self.resumes_by_id: dict[str, Resume] = {}

    def rebuild(self, resumes: list[Resume] | None = None) -> None:
        resumes = resumes if resumes is not None else load_resumes()
        self.resumes_by_id = {resume.id: resume for resume in resumes}
        self.resume_ids = [resume.id for resume in resumes]
        embeddings = _load_cached_embeddings(resumes)
        if embeddings is None:
            texts = [resume.raw_text for resume in resumes]
            embeddings = (
                get_embedding_service().encode(texts)
                if texts
                else np.zeros((0, EMBEDDING_DIMENSION), dtype="float32")
            )
            _save_cached_embeddings(resumes, embeddings)
        self.index = _build_index(embeddings)

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        all_resumes = load_resumes()
        if self.index is None or len(self.resume_ids) != len(all_resumes):
            self.rebuild(all_resumes)
        if not self.resume_ids:
            return []
        query_embedding = get_embedding_service().encode([query])
        scores, indices = self.index.search(query_embedding, min(top_k, len(self.resume_ids)))
        results: list[SearchResult] = []
        for score, index in zip(scores[0], indices[0], strict=False):
            if index < 0:
                continue
            resume = self.resumes_by_id[self.resume_ids[index]]
            results.append(SearchResult(resume=resume, similarity=round(float(score), 4)))
        return results

    def similarities_for_job(self, job_text: str, resumes: list[Resume]) -> dict[str, float]:
        if not resumes:
            return {}
        resume_embeddings = get_embedding_service().encode([resume.raw_text for resume in resumes])
        job_embedding = get_embedding_service().encode([job_text])[0]
        scores = resume_embeddings @ job_embedding
        return {resume.id: float(score) for resume, score in zip(resumes, scores, strict=False)}


def _build_index(embeddings: np.ndarray):
    try:
        import faiss

        index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
        if len(embeddings):
            index.add(embeddings)
        return index
    except Exception:  # pragma: no cover - used only when FAISS is unavailable
        return NumpyIndex(embeddings)


def _load_cached_embeddings(resumes: list[Resume]) -> np.ndarray | None:
    if not EMBEDDINGS_PATH.exists() or not METADATA_PATH.exists():
        return None
    try:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        if metadata.get("fingerprint") != _resume_fingerprint(resumes):
            return None
        embeddings = np.load(EMBEDDINGS_PATH)
        if embeddings.shape != (len(resumes), EMBEDDING_DIMENSION):
            return None
        return embeddings.astype("float32")
    except Exception:
        return None


def _save_cached_embeddings(resumes: list[Resume], embeddings: np.ndarray) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDINGS_PATH, embeddings.astype("float32"))
    METADATA_PATH.write_text(
        json.dumps(
            {
                "fingerprint": _resume_fingerprint(resumes),
                "count": len(resumes),
                "dimension": EMBEDDING_DIMENSION,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _resume_fingerprint(resumes: list[Resume]) -> str:
    digest = hashlib.sha256()
    for resume in resumes:
        digest.update(resume.id.encode("utf-8"))
        digest.update(str(len(resume.raw_text)).encode("utf-8"))
        digest.update(resume.raw_text[:500].encode("utf-8"))
    return digest.hexdigest()


class NumpyIndex:
    def __init__(self, embeddings: np.ndarray) -> None:
        self.embeddings = embeddings

    def search(self, query_embedding: np.ndarray, top_k: int):
        if len(self.embeddings) == 0:
            return np.array([[]]), np.array([[]])
        scores = self.embeddings @ query_embedding[0]
        order = np.argsort(scores)[::-1][:top_k]
        return np.array([scores[order]]), np.array([order])


@lru_cache(maxsize=1)
def get_search_service() -> SearchService:
    return SearchService()

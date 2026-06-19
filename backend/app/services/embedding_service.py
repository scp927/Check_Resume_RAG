from __future__ import annotations

import hashlib
import math
import os
from functools import lru_cache
from threading import Lock

import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


class EmbeddingService:
    """Local MiniLM embedding service.

    Production/runtime search uses sentence-transformers/all-MiniLM-L6-v2.
    A deterministic fallback is available only when explicitly enabled with
    ATS_ALLOW_EMBEDDING_FALLBACK=1 for lightweight smoke tests.
    """

    def __init__(self) -> None:
        self._model = None
        self._load_error: Exception | None = None
        self._lock = Lock()

    @property
    def model(self):
        with self._lock:
            if self._model is None and self._load_error is None:
                try:
                    from sentence_transformers import SentenceTransformer

                    self._model = SentenceTransformer(MODEL_NAME)
                except Exception as exc:  # pragma: no cover - depends on local model install
                    self._load_error = exc
            return self._model

    def encode(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        clean_texts = [text or "" for text in texts]
        if self._fallback_allowed():
            return np.vstack([self._hash_embedding(text) for text in clean_texts]).astype("float32")
        model = self.model
        if model is not None:
            with self._lock:
                embeddings = model.encode(
                    clean_texts,
                    batch_size=batch_size,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                return embeddings.astype("float32")
        raise RuntimeError(
            f"MiniLM embedding model is required but could not be loaded: {self._load_error}. "
            "Install backend requirements, then rerun the server. For tests only, set "
            "ATS_ALLOW_EMBEDDING_FALLBACK=1."
        )

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]

    def using_fallback(self) -> bool:
        return self._fallback_allowed()

    def model_name(self) -> str:
        return MODEL_NAME

    def _fallback_allowed(self) -> bool:
        return os.getenv("ATS_ALLOW_EMBEDDING_FALLBACK") == "1"

    def _hash_embedding(self, text: str) -> np.ndarray:
        tokens = [token.strip(".,;:()[]{}").lower() for token in text.split()]
        vector = np.zeros(EMBEDDING_DIMENSION, dtype="float32")
        for token in tokens:
            if not token:
                continue
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % EMBEDDING_DIMENSION
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(float(np.dot(vector, vector)))
        if norm == 0:
            return vector
        return vector / norm


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

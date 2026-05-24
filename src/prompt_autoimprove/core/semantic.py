from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


class SemanticUnavailable(Exception):
    pass


@runtime_checkable
class SemanticSimilarity(Protocol):
    def similarity(self, left: str, right: str) -> float: ...


def _cosine(left: list[float], right: list[float]) -> float:
    left_norm = math.sqrt(sum(v * v for v in left))
    right_norm = math.sqrt(sum(v * v for v in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    return dot / (left_norm * right_norm)


@dataclass(slots=True)
class EmbeddingSimilarity:
    """Cosine similarity of sentence embeddings; loads the model lazily (ml group)."""

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"
    _model: Any = field(init=False, default=None, repr=False)

    def _ensure_ready(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise SemanticUnavailable("install: uv sync --group ml") from exc
        self._model = SentenceTransformer(self.model_name, device=self.device)

    def _encode(self, text: str) -> list[float]:
        vector = self._model.encode(text, convert_to_numpy=True)
        return list(map(float, vector.tolist()))

    def similarity(self, left: str, right: str) -> float:
        self._ensure_ready()
        score = _cosine(self._encode(left), self._encode(right))
        return max(0.0, min(1.0, score))

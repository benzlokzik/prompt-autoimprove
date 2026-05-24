from __future__ import annotations

import asyncio
import hashlib
import math
import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from prompt_autoimprove.adapters.base import GenerationRequest, ModelAdapter
from prompt_autoimprove.core._complexity_exemplars import HARD_EXEMPLARS, SIMPLE_EXEMPLARS
from prompt_autoimprove.core.complexity import ComplexityVerdict

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from prompt_autoimprove.domain.prompt import NormalizedPrompt

_MAX_CACHE_ENTRIES = 512


def _run_coroutine_blocking[T](coro: Coroutine[Any, Any, T]) -> T:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    # Already inside a loop: run the coroutine to completion on a private loop in a
    # worker thread so the synchronous caller still gets a value without nesting loops.
    result: list[T] = []
    error: list[BaseException] = []

    def _worker() -> None:
        try:
            result.append(asyncio.run(coro))
        except BaseException as exc:
            error.append(exc)

    thread = threading.Thread(target=_worker)
    thread.start()
    thread.join()
    if error:
        raise error[0]
    return result[0]


class ClassifierUnavailable(Exception):
    pass


def _mean_pool(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return []
    width = len(vectors[0])
    pooled = [0.0] * width
    for vector in vectors:
        for idx, value in enumerate(vector):
            pooled[idx] += value
    return [value / len(vectors) for value in pooled]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    dot = sum(l_value * r_value for l_value, r_value in zip(left, right, strict=True))
    return dot / (left_norm * right_norm)


def _softmax_pair(left: float, right: float) -> tuple[float, float]:
    max_value = max(left, right)
    left_exp = math.exp(left - max_value)
    right_exp = math.exp(right - max_value)
    denom = left_exp + right_exp
    return left_exp / denom, right_exp / denom


@dataclass(slots=True)
class EmbeddingClassifier:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"
    eager: bool = False
    name: str = "embedding-classifier"
    _model: Any = field(init=False, default=None, repr=False)
    _simple_centroid: list[float] | None = field(init=False, default=None, repr=False)
    _hard_centroid: list[float] | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        if self.eager:
            self._ensure_ready()

    def _ensure_ready(self) -> None:
        if (
            self._model is not None
            and self._simple_centroid is not None
            and self._hard_centroid is not None
        ):
            return
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ClassifierUnavailable("install: uv sync --group ml") from exc
        self._model = SentenceTransformer(self.model_name, device=self.device)
        simple_vectors = self._encode_many(SIMPLE_EXEMPLARS)
        hard_vectors = self._encode_many(HARD_EXEMPLARS)
        self._simple_centroid = _mean_pool(simple_vectors)
        self._hard_centroid = _mean_pool(hard_vectors)

    def _encode_many(self, texts: tuple[str, ...]) -> list[list[float]]:
        vectors = self._model.encode(texts, convert_to_numpy=True)
        return [list(map(float, vector.tolist())) for vector in vectors]

    def _encode_one(self, text: str) -> list[float]:
        vector = self._model.encode(text, convert_to_numpy=True)
        return list(map(float, vector.tolist()))

    def classify(self, normalized: NormalizedPrompt) -> ComplexityVerdict:
        self._ensure_ready()
        vector = self._encode_one(normalized.cleaned_text)
        simple_sim = _cosine_similarity(vector, self._simple_centroid or [])
        hard_sim = _cosine_similarity(vector, self._hard_centroid or [])
        _, hard_prob = _softmax_pair(simple_sim, hard_sim)
        label: Literal["simple", "hard"] = "hard" if hard_prob >= 0.5 else "simple"
        reasons = (f"embedding_sim(simple={simple_sim:.3f},hard={hard_sim:.3f})",)
        return ComplexityVerdict(label=label, score=hard_prob, reasons=reasons)


@dataclass(slots=True)
class JudgeClassifier:
    judge: ModelAdapter
    max_output_tokens: int = 16
    name: str = "judge-classifier"
    _cache: dict[str, ComplexityVerdict] = field(init=False, default_factory=dict, repr=False)

    async def classify_async(self, normalized: NormalizedPrompt) -> ComplexityVerdict:
        key = self._key(normalized)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        verdict = await self._classify_async(normalized)
        self._store(key, verdict)
        return verdict

    def classify(self, normalized: NormalizedPrompt) -> ComplexityVerdict:
        key = self._key(normalized)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        verdict = _run_coroutine_blocking(self._classify_async(normalized))
        self._store(key, verdict)
        return verdict

    def _key(self, normalized: NormalizedPrompt) -> str:
        return hashlib.sha256(f"{normalized.cleaned_text}{self.judge.name}".encode()).hexdigest()[
            :32
        ]

    def _store(self, key: str, verdict: ComplexityVerdict) -> None:
        if len(self._cache) >= _MAX_CACHE_ENTRIES:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = verdict

    async def _classify_async(self, normalized: NormalizedPrompt) -> ComplexityVerdict:
        request = GenerationRequest(
            prompt=(
                "Classify the following user request as `simple` or `hard` based on "
                "whether it needs multi-step reasoning. Reply with EXACTLY one word: "
                "simple or hard.\n\n"
                f"Request:\n{normalized.cleaned_text}\n\n"
                "Classification:"
            ),
            max_tokens=self.max_output_tokens,
            temperature=0.2,
        )
        result = await self.judge.generate(request)
        token = result.text.strip().split(maxsplit=1)[0].lower() if result.text.strip() else ""
        if token == "hard":
            return ComplexityVerdict(label="hard", score=1.0, reasons=("judge_label(hard)",))
        if token == "simple":
            return ComplexityVerdict(label="simple", score=0.0, reasons=("judge_label(simple)",))
        return ComplexityVerdict(
            label="simple",
            score=0.0,
            reasons=(f"judge_unparseable({token})",),
        )

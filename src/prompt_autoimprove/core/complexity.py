from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from prompt_autoimprove.domain.task_type import TaskType

if TYPE_CHECKING:
    from prompt_autoimprove.adapters.base import ModelAdapter
    from prompt_autoimprove.config import ClassifierSettings
    from prompt_autoimprove.domain.prompt import NormalizedPrompt

Complexity = Literal["simple", "hard"]

_HARD_TASKS: frozenset[str] = frozenset(
    {
        TaskType.CODE_GENERATE.value,
        TaskType.REASONING.value,
        TaskType.EXTRACT.value,
    }
)

_LONG_CHAR_THRESHOLD = 600
_VERY_LONG_CHAR_THRESHOLD = 1000
_LONG_LINE_THRESHOLD = 6
_MANY_PARAMS_THRESHOLD = 2
HEURISTIC_HARD_THRESHOLD = 0.45


@dataclass(slots=True, frozen=True)
class ComplexityVerdict:
    label: Complexity
    score: float
    reasons: tuple[str, ...]


@runtime_checkable
class ComplexityClassifier(Protocol):
    name: str

    def classify(self, normalized: NormalizedPrompt) -> ComplexityVerdict: ...


def heuristic_score(normalized: NormalizedPrompt) -> tuple[float, list[str]]:
    reasons: list[str] = []
    score = 0.0

    char_len = len(normalized.cleaned_text)
    if char_len >= _LONG_CHAR_THRESHOLD:
        score += 0.35
        reasons.append(f"long_text({char_len}c)")
    if char_len >= _VERY_LONG_CHAR_THRESHOLD:
        score += 0.20
        reasons.append("very_long_text")

    line_count = normalized.cleaned_text.count("\n") + 1
    if line_count >= _LONG_LINE_THRESHOLD:
        score += 0.15
        reasons.append(f"many_lines({line_count})")

    if normalized.detected_task in _HARD_TASKS:
        score += 0.40
        reasons.append(f"hard_task({normalized.detected_task})")

    if len(normalized.missing_parameters) >= _MANY_PARAMS_THRESHOLD:
        score += 0.20
        reasons.append(f"unfilled_params({len(normalized.missing_parameters)})")

    lowered = normalized.cleaned_text.lower()
    if lowered.count("?") >= 3:
        score += 0.10
        reasons.append("multi_question")
    if any(marker in lowered for marker in (" and also ", " then ", " finally ")):
        score += 0.05
        reasons.append("multi_step_marker")

    return score, reasons


@dataclass(slots=True)
class HeuristicClassifier:
    name: str = "heuristic"

    def classify(self, normalized: NormalizedPrompt) -> ComplexityVerdict:
        score, reasons = heuristic_score(normalized)
        label: Complexity = "hard" if score >= HEURISTIC_HARD_THRESHOLD else "simple"
        return ComplexityVerdict(label=label, score=round(score, 3), reasons=tuple(reasons))


@dataclass(slots=True)
class CompositeClassifier:
    ml: ComplexityClassifier
    heuristic: HeuristicClassifier
    lo: float = 0.30
    hi: float = 0.55
    name: str = "composite"

    def classify(self, normalized: NormalizedPrompt) -> ComplexityVerdict:
        h = self.heuristic.classify(normalized)
        # Decisive heuristic verdicts short-circuit so the ML backend only runs in the
        # uncertain band — keeps cost / latency bounded.
        if h.score < self.lo or h.score > self.hi:
            return h
        ml = self.ml.classify(normalized)
        merged_reasons = (*h.reasons, f"composite_band({h.score})", *ml.reasons)
        return ComplexityVerdict(label=ml.label, score=ml.score, reasons=merged_reasons)


def classify(normalized: NormalizedPrompt) -> ComplexityVerdict:
    return HeuristicClassifier().classify(normalized)


def build_classifier(
    settings: ClassifierSettings | None = None,
    *,
    improver: ModelAdapter | None = None,
) -> ComplexityClassifier:
    if settings is None or settings.backend == "heuristic":
        return HeuristicClassifier()

    if settings.backend == "judge":
        if improver is None:
            return HeuristicClassifier()
        from prompt_autoimprove.core.ml_complexity import JudgeClassifier

        return JudgeClassifier(judge=improver)

    from prompt_autoimprove.core.ml_complexity import EmbeddingClassifier

    embeddings = EmbeddingClassifier(model_name=settings.embedding_model, device=settings.device)
    if settings.backend == "embeddings":
        return embeddings
    if settings.backend == "composite":
        return CompositeClassifier(
            ml=embeddings,
            heuristic=HeuristicClassifier(),
            lo=settings.composite_lo,
            hi=settings.composite_hi,
        )
    return HeuristicClassifier()

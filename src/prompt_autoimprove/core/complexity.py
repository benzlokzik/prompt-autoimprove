"""Heuristic complexity classifier (Tier A).

Decides whether a normalized prompt should be escalated to the LLM-powered
rewrite path. Pure-Python, zero deps, deterministic — safe to run in-process
on every request.
"""

from dataclasses import dataclass
from typing import Literal

from prompt_autoimprove.domain.prompt import NormalizedPrompt
from prompt_autoimprove.domain.task_type import TaskType

Complexity = Literal["simple", "hard"]

_HARD_TASKS: frozenset[str] = frozenset(
    {
        TaskType.CODE_GENERATE.value,
        TaskType.REASONING.value,
        TaskType.EXTRACT.value,
    }
)

_LONG_CHAR_THRESHOLD = 600
_LONG_LINE_THRESHOLD = 6
_MANY_PARAMS_THRESHOLD = 2


@dataclass(slots=True, frozen=True)
class ComplexityVerdict:
    label: Complexity
    score: float
    reasons: tuple[str, ...]


def classify(normalized: NormalizedPrompt) -> ComplexityVerdict:
    """Score the prompt on a few orthogonal axes; ≥0.5 ⇒ ``hard``."""
    reasons: list[str] = []
    score = 0.0

    char_len = len(normalized.cleaned_text)
    if char_len >= _LONG_CHAR_THRESHOLD:
        score += 0.35
        reasons.append(f"long_text({char_len}c)")

    line_count = normalized.cleaned_text.count("\n") + 1
    if line_count >= _LONG_LINE_THRESHOLD:
        score += 0.15
        reasons.append(f"many_lines({line_count})")

    if normalized.detected_task in _HARD_TASKS:
        score += 0.30
        reasons.append(f"hard_task({normalized.detected_task})")

    if len(normalized.missing_parameters) >= _MANY_PARAMS_THRESHOLD:
        score += 0.20
        reasons.append(f"unfilled_params({len(normalized.missing_parameters)})")

    # Ambiguity signals: questions stacked, conditionals, multiple imperatives.
    lowered = normalized.cleaned_text.lower()
    if lowered.count("?") >= 3:
        score += 0.10
        reasons.append("multi_question")
    if any(marker in lowered for marker in (" and also ", " then ", " finally ")):
        score += 0.05
        reasons.append("multi_step_marker")

    label: Complexity = "hard" if score >= 0.5 else "simple"
    return ComplexityVerdict(label=label, score=round(score, 3), reasons=tuple(reasons))

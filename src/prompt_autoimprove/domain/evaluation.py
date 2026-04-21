"""Evaluation entities: per-metric results and the integrated score."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class MetricName(StrEnum):
    CLARITY = "q_c"
    PROMPT_COMPLIANCE = "q_p"
    SAFETY = "q_s"
    TOKEN_COST = "q_t"
    LATENCY = "q_l"


@dataclass(slots=True, frozen=True)
class EvaluationMetric:
    """A single metric value, normalized to [0, 1]."""

    name: MetricName
    value: float
    raw_value: float
    weight: float


@dataclass(slots=True, frozen=True)
class Score:
    """Aggregate score and the components that produced it."""

    integrated: float
    metrics: tuple[EvaluationMetric, ...]


@dataclass(slots=True)
class EvaluationRun:
    """One evaluation pass for a candidate revision against a profile."""

    revision_id: UUID
    profile_name: str
    score: Score
    explanation: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

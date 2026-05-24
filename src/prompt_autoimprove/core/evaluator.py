from dataclasses import dataclass

from prompt_autoimprove.core.strategies.base import CandidatePrompt
from prompt_autoimprove.core.validator import ValidationReport
from prompt_autoimprove.domain.evaluation import EvaluationMetric, MetricName, Score
from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.task_type import REASONING_HEAVY

DEFAULT_WEIGHTS: dict[MetricName, float] = {
    MetricName.CLARITY: 0.30,
    MetricName.PROMPT_COMPLIANCE: 0.25,
    MetricName.SAFETY: 0.20,
    MetricName.TOKEN_COST: 0.15,
    MetricName.LATENCY: 0.10,
}

# Local models are cheap to run but slow and context-bound, so weight cost and
# latency higher; reasoning-heavy tasks reward a clear, faithful prompt more.
_LOCAL_EMPHASIS = 1.5
_REASONING_EMPHASIS = 1.3
_REASONING_TASKS: frozenset[str] = frozenset(t.value for t in REASONING_HEAVY)


def _clip(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def resolve_weights(
    base: dict[MetricName, float],
    profile: ModelProfile,
    task: str | None,
) -> dict[MetricName, float]:
    """Adjust the base weight vector for a profile/task; not yet normalized."""
    w = dict(base)
    if profile.is_local:
        w[MetricName.TOKEN_COST] *= _LOCAL_EMPHASIS
        w[MetricName.LATENCY] *= _LOCAL_EMPHASIS
    if task is not None and task in _REASONING_TASKS:
        w[MetricName.CLARITY] *= _REASONING_EMPHASIS
        w[MetricName.PROMPT_COMPLIANCE] *= _REASONING_EMPHASIS
    return w


@dataclass(slots=True)
class IntegratedScorer:
    weights: dict[MetricName, float] = None  # type: ignore[assignment]
    profile_aware: bool = True

    def __post_init__(self) -> None:
        if self.weights is None:
            self.weights = dict(DEFAULT_WEIGHTS)
        total = sum(self.weights.values())
        if total <= 0:
            raise ValueError("weights must sum to a positive number")
        self.weights = {k: v / total for k, v in self.weights.items()}

    def _weights_for(self, profile: ModelProfile, task: str | None) -> dict[MetricName, float]:
        if not self.profile_aware:
            return self.weights
        resolved = resolve_weights(self.weights, profile, task)
        total = sum(resolved.values())
        return {k: v / total for k, v in resolved.items()}

    def score(
        self,
        candidate: CandidatePrompt,
        profile: ModelProfile,
        report: ValidationReport,
        *,
        task: str | None = None,
        target_latency_ms: int = 5000,
    ) -> Score:
        text = candidate.text
        clarity_raw = self._clarity(text)
        compliance_raw = self._compliance(text, candidate.rationale)
        safety_raw = self._safety(report)
        cost_raw = self._cost(candidate.estimated_tokens, profile)
        latency_raw = self._latency(profile, target_latency_ms)

        components = {
            MetricName.CLARITY: clarity_raw,
            MetricName.PROMPT_COMPLIANCE: compliance_raw,
            MetricName.SAFETY: safety_raw,
            MetricName.TOKEN_COST: cost_raw,
            MetricName.LATENCY: latency_raw,
        }

        weights = self._weights_for(profile, task)
        metrics = tuple(
            EvaluationMetric(
                name=name,
                value=_clip(raw),
                raw_value=raw,
                weight=weights[name],
            )
            for name, raw in components.items()
        )
        integrated = sum(m.value * m.weight for m in metrics)
        return Score(integrated=integrated, metrics=metrics)

    @staticmethod
    def _clarity(text: str) -> float:
        markers = ["You are ", "Output contract", "phases", "Return only", "Schema:"]
        hits = sum(1 for m in markers if m in text)
        length_factor = 1.0 if 50 <= len(text) <= 4000 else 0.6
        return min(1.0, 0.3 + 0.15 * hits) * length_factor

    @staticmethod
    def _compliance(text: str, rationale: str) -> float:
        coverage = 0.5
        if "User request" in text or "Now solve" in text or "Task:" in text:
            coverage += 0.25
        if rationale:
            coverage += 0.15
        if any(w in text.lower() for w in ("must", "only", "exactly")):
            coverage += 0.1
        return coverage

    @staticmethod
    def _safety(report: ValidationReport) -> float:
        if not report.ok:
            return 0.0
        warnings = sum(1 for i in report.issues if i.severity == "warning")
        return max(0.0, 1.0 - 0.1 * warnings)

    @staticmethod
    def _cost(tokens: int, profile: ModelProfile) -> float:
        if profile.context_window <= 0:
            return 0.0
        ratio = tokens / profile.context_window
        return 1.0 - min(ratio, 1.0)

    @staticmethod
    def _latency(profile: ModelProfile, target_ms: int) -> float:
        if profile.p50_latency_ms <= 0:
            return 0.8
        return _clip(target_ms / max(profile.p50_latency_ms, 1))

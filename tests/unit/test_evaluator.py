import math

import pytest

from prompt_autoimprove.core.evaluator import DEFAULT_WEIGHTS, IntegratedScorer
from prompt_autoimprove.core.strategies.base import CandidatePrompt, estimate_tokens
from prompt_autoimprove.core.validator import ValidationIssue, ValidationReport
from prompt_autoimprove.domain.evaluation import MetricName
from prompt_autoimprove.domain.model_profile import ModelFamily, ModelFormat, ModelProfile
from prompt_autoimprove.domain.strategy import StrategyName


def _profile(ctx: int = 4096, latency: int = 5000) -> ModelProfile:
    return ModelProfile(
        name="qwen3-test",
        family=ModelFamily.QWEN,
        format=ModelFormat.GGUF,
        context_window=ctx,
        max_output_tokens=1024,
        p50_latency_ms=latency,
    )


def _candidate(text: str = "You are an expert. Output contract: json. Task: hi") -> CandidatePrompt:
    return CandidatePrompt(
        text=text,
        strategy=StrategyName.ROLE_BASED,
        rationale="r",
        estimated_tokens=estimate_tokens(text),
    )


def test_default_weights_sum_to_one() -> None:
    assert math.isclose(sum(DEFAULT_WEIGHTS.values()), 1.0, abs_tol=1e-9)


def test_score_in_unit_interval() -> None:
    scorer = IntegratedScorer()
    report = ValidationReport(candidate_id="x", issues=())
    score = scorer.score(_candidate(), _profile(), report)
    assert 0.0 <= score.integrated <= 1.0
    assert {m.name for m in score.metrics} == set(MetricName)


def test_safety_zero_when_validation_fails() -> None:
    scorer = IntegratedScorer()
    bad = ValidationReport(
        candidate_id="x",
        issues=(ValidationIssue("unsafe", "bad", severity="error"),),
    )
    score = scorer.score(_candidate(), _profile(), bad)
    safety = next(m for m in score.metrics if m.name is MetricName.SAFETY)
    assert safety.value == 0.0


def test_cost_drops_with_long_prompt() -> None:
    scorer = IntegratedScorer()
    report = ValidationReport(candidate_id="x", issues=())
    short = scorer.score(_candidate("a" * 100), _profile(ctx=4096), report)
    long = scorer.score(_candidate("a" * 4000), _profile(ctx=4096), report)
    short_cost = next(m for m in short.metrics if m.name is MetricName.TOKEN_COST).value
    long_cost = next(m for m in long.metrics if m.name is MetricName.TOKEN_COST).value
    assert short_cost > long_cost


def test_custom_weights_are_renormalized() -> None:
    scorer = IntegratedScorer(weights=dict.fromkeys(MetricName, 1.0))
    total = sum(scorer.weights.values())
    assert math.isclose(total, 1.0, abs_tol=1e-9)


def test_zero_weights_rejected() -> None:
    with pytest.raises(ValueError):
        IntegratedScorer(weights=dict.fromkeys(MetricName, 0.0))

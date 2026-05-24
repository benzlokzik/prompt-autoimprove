from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from prompt_autoimprove.core.evaluator import DEFAULT_WEIGHTS, IntegratedScorer
from prompt_autoimprove.core.strategies.base import CandidatePrompt, estimate_tokens
from prompt_autoimprove.core.validator import validate
from prompt_autoimprove.domain.strategy import StrategyName
from prompt_autoimprove.registry.loader import load_profiles

_PROFILES = load_profiles(
    Path(__file__).resolve().parents[2] / "src/prompt_autoimprove/registry/profiles"
)
_PROFILE = next(iter(_PROFILES.values()))


@given(text=st.text(min_size=0, max_size=2000))
def test_integrated_score_stays_in_unit_interval(text: str) -> None:
    candidate = CandidatePrompt(
        text=text,
        strategy=StrategyName.ROLE_BASED,
        rationale="prop-test",
        estimated_tokens=estimate_tokens(text),
    )
    report = validate(candidate, _PROFILE)
    score = IntegratedScorer().score(candidate, _PROFILE, report)
    assert 0.0 <= score.integrated <= 1.0
    assert all(0.0 <= m.value <= 1.0 for m in score.metrics)


@given(
    weights=st.lists(st.floats(min_value=0.01, max_value=100.0), min_size=5, max_size=5),
)
def test_weights_are_normalized(weights: list[float]) -> None:
    mapping = dict(zip(DEFAULT_WEIGHTS.keys(), weights, strict=True))
    scorer = IntegratedScorer(weights=mapping)
    assert abs(sum(scorer.weights.values()) - 1.0) < 1e-9

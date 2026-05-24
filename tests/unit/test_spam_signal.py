import pytest

from prompt_autoimprove.core.evaluator import IntegratedScorer, _spam_score
from prompt_autoimprove.core.normalizer import normalize
from prompt_autoimprove.core.spam_signal import BertSpamSignal, SpamSignal, SpamUnavailable
from prompt_autoimprove.core.strategies.base import CandidatePrompt, estimate_tokens
from prompt_autoimprove.core.validator import ValidationReport
from prompt_autoimprove.domain.model_profile import ModelFamily, ModelFormat, ModelProfile
from prompt_autoimprove.domain.prompt import Prompt
from prompt_autoimprove.domain.strategy import StrategyName


class _FakeSpam:
    def __init__(self, value: float) -> None:
        self.value = value
        self.calls: list[str] = []

    def score(self, text: str) -> float:
        self.calls.append(text)
        return self.value


class _BoomSpam:
    def score(self, text: str) -> float:
        raise RuntimeError("model exploded")


def test_fake_scorer_satisfies_protocol() -> None:
    assert isinstance(_FakeSpam(0.5), SpamSignal)


def test_bert_signal_unavailable_without_dependency() -> None:
    # spam_detector is not installed in the dev environment.
    with pytest.raises(SpamUnavailable):
        BertSpamSignal().score("привет")


def test_normalize_flags_russian_spam() -> None:
    scorer = _FakeSpam(0.91)
    result = normalize(Prompt(text="Купите дешёвые таблетки прямо сейчас"), spam_scorer=scorer)
    assert "spam:0.9100" in result.safety_flags
    assert scorer.calls  # the scorer was actually consulted


def test_normalize_skips_english_text() -> None:
    scorer = _FakeSpam(0.99)
    result = normalize(Prompt(text="Buy cheap pills right now"), spam_scorer=scorer)
    assert not any(f.startswith("spam:") for f in result.safety_flags)
    assert scorer.calls == []


def test_normalize_without_scorer_is_unchanged() -> None:
    text = "Купите дешёвые таблетки прямо сейчас"
    baseline = normalize(Prompt(text=text)).safety_flags
    assert not any(f.startswith("spam:") for f in baseline)


def test_normalize_degrades_on_scorer_failure() -> None:
    result = normalize(Prompt(text="Срочное предложение только сегодня"), spam_scorer=_BoomSpam())
    assert not any(f.startswith("spam:") for f in result.safety_flags)


def test_spam_score_parser() -> None:
    assert _spam_score(("pii:email", "spam:0.7500")) == pytest.approx(0.75)
    assert _spam_score(("pii:email",)) is None
    assert _spam_score(("spam:not-a-number",)) is None


def _profile() -> ModelProfile:
    return ModelProfile(
        name="qwen3-test",
        family=ModelFamily.QWEN,
        format=ModelFormat.GGUF,
        context_window=4096,
        max_output_tokens=1024,
        p50_latency_ms=5000,
    )


def _candidate() -> CandidatePrompt:
    text = "You are an expert. Task: hi"
    return CandidatePrompt(
        text=text,
        strategy=StrategyName.ROLE_BASED,
        rationale="r",
        estimated_tokens=estimate_tokens(text),
    )


def test_safety_penalty_scales_with_spam_and_weight() -> None:
    report = ValidationReport(candidate_id="x", issues=())
    clean = IntegratedScorer()._safety(report)
    penalized = IntegratedScorer(moderation_weight=0.5)._safety(report, ("spam:1.0",))
    assert penalized == pytest.approx(clean * 0.5)


def test_safety_penalty_absent_without_flag() -> None:
    report = ValidationReport(candidate_id="x", issues=())
    assert IntegratedScorer(moderation_weight=0.9)._safety(report, ("pii:email",)) == pytest.approx(
        IntegratedScorer()._safety(report)
    )


def test_spam_flag_lowers_integrated_score() -> None:
    report = ValidationReport(candidate_id="x", issues=())
    scorer = IntegratedScorer(moderation_weight=0.8)
    base = scorer.score(_candidate(), _profile(), report)
    flagged = scorer.score(_candidate(), _profile(), report, safety_flags=("spam:0.9",))
    assert flagged.integrated < base.integrated

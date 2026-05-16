from dataclasses import dataclass

from prompt_autoimprove.config import ClassifierSettings
from prompt_autoimprove.core.complexity import (
    ComplexityVerdict,
    CompositeClassifier,
    HeuristicClassifier,
    build_classifier,
    classify,
)
from prompt_autoimprove.core.normalizer import normalize
from prompt_autoimprove.domain.prompt import Prompt


@dataclass(slots=True)
class _SpyClassifier:
    name: str = "spy"
    calls: int = 0
    label: str = "hard"

    def classify(self, normalized):
        _ = normalized
        self.calls += 1
        return ComplexityVerdict(
            label=self.label,  # type: ignore[arg-type]
            score=0.99,
            reasons=("spy",),
        )


def _norm(text: str):
    return normalize(Prompt(text=text))


def test_legacy_classify_still_returns_verdict() -> None:
    verdict = classify(_norm("translate hello to french"))
    assert verdict.label == "simple"


def test_composite_short_circuits_when_heuristic_low() -> None:
    spy = _SpyClassifier()
    cls = CompositeClassifier(ml=spy, heuristic=HeuristicClassifier(), lo=0.30, hi=0.55)
    verdict = cls.classify(_norm("translate hello to french"))
    assert verdict.label == "simple"
    assert spy.calls == 0


def test_composite_short_circuits_when_heuristic_high() -> None:
    spy = _SpyClassifier(label="simple")
    cls = CompositeClassifier(ml=spy, heuristic=HeuristicClassifier(), lo=0.30, hi=0.55)
    big = "Refactor this billing code step by step prove correctness " + "more " * 200
    verdict = cls.classify(_norm(big))
    # Heuristic decisively hard (very_long_text + reasoning task) → ML skipped.
    assert verdict.label == "hard"
    assert spy.calls == 0


def test_composite_consults_ml_in_borderline_band() -> None:
    @dataclass(slots=True)
    class _StubHeuristic:
        name: str = "stub-heuristic"

        def classify(self, normalized):
            _ = normalized
            return ComplexityVerdict(label="simple", score=0.40, reasons=("stub",))

    spy = _SpyClassifier(label="hard")
    cls = CompositeClassifier(ml=spy, heuristic=_StubHeuristic(), lo=0.30, hi=0.55)  # type: ignore[arg-type]
    verdict = cls.classify(_norm("any prompt"))
    assert spy.calls == 1
    assert verdict.label == "hard"
    assert "stub" in verdict.reasons
    assert "spy" in verdict.reasons


def test_build_classifier_default_is_heuristic() -> None:
    assert isinstance(build_classifier(None), HeuristicClassifier)
    assert isinstance(build_classifier(ClassifierSettings()), HeuristicClassifier)


def test_build_classifier_judge_falls_back_without_improver() -> None:
    settings = ClassifierSettings(backend="judge")
    cls = build_classifier(settings, improver=None)
    assert isinstance(cls, HeuristicClassifier)

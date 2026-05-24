import pytest

from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.core.semantic import EmbeddingSimilarity, SemanticUnavailable
from prompt_autoimprove.core.strategies.base import CandidatePrompt, estimate_tokens
from prompt_autoimprove.core.validator import ValidationReport
from prompt_autoimprove.domain.evaluation import MetricName
from prompt_autoimprove.domain.model_profile import ModelFamily, ModelFormat, ModelProfile
from prompt_autoimprove.domain.strategy import StrategyName


class _FakeSemantic:
    def __init__(self, value: float) -> None:
        self.value = value

    def similarity(self, left: str, right: str) -> float:
        return self.value


def _profile() -> ModelProfile:
    return ModelProfile(
        name="p",
        family=ModelFamily.QWEN,
        format=ModelFormat.API,
        context_window=4096,
        max_output_tokens=512,
    )


def _candidate(text: str = "Do the task exactly as asked.") -> CandidatePrompt:
    return CandidatePrompt(
        text=text,
        strategy=StrategyName.ROLE_BASED,
        rationale="r",
        estimated_tokens=estimate_tokens(text),
    )


def _compliance(score) -> float:
    return next(m for m in score.metrics if m.name is MetricName.PROMPT_COMPLIANCE).value


def _score(semantic, reference):
    return IntegratedScorer(semantic=semantic, profile_aware=False).score(
        _candidate(), _profile(), ValidationReport(candidate_id="x", issues=()), reference=reference
    )


def test_higher_similarity_lifts_compliance() -> None:
    low = _score(_FakeSemantic(0.0), "do the task")
    high = _score(_FakeSemantic(1.0), "do the task")
    assert _compliance(high) > _compliance(low)
    assert 0.0 <= high.integrated <= 1.0


def test_no_reference_keeps_pure_heuristic() -> None:
    assert _compliance(_score(_FakeSemantic(1.0), None)) == _compliance(_score(None, "ref"))


def test_semantic_failure_falls_back_to_heuristic() -> None:
    class Boom:
        def similarity(self, left: str, right: str) -> float:
            raise RuntimeError("model down")

    assert _compliance(_score(Boom(), "ref")) == _compliance(_score(None, "ref"))


def test_embedding_similarity_unavailable_without_ml() -> None:
    try:
        import sentence_transformers  # noqa: F401

        pytest.skip("sentence-transformers installed; unavailable-path not applicable")
    except ImportError:
        pass
    with pytest.raises(SemanticUnavailable):
        EmbeddingSimilarity().similarity("a", "b")

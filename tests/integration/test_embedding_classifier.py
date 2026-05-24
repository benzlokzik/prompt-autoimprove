import pytest

from prompt_autoimprove.core.normalizer import normalize
from prompt_autoimprove.domain.prompt import Prompt

pytest.importorskip("sentence_transformers")

from prompt_autoimprove.core.ml_complexity import EmbeddingClassifier


@pytest.fixture(scope="module")
def classifier() -> EmbeddingClassifier:
    return EmbeddingClassifier(eager=True)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("translate hello to french", "simple"),
        ("what does HTTP 429 mean?", "simple"),
        (
            "Refactor this billing service step by step and prove correctness across edge cases.",
            "hard",
        ),
        ("Design a multi-region failover plan for a payments API with rollback steps.", "hard"),
    ],
)
def test_embedding_classifier_matches_expectation(
    classifier: EmbeddingClassifier, text: str, expected: str
) -> None:
    verdict = classifier.classify(normalize(Prompt(text=text)))
    assert verdict.label == expected, (
        f"got={verdict.label} score={verdict.score:.3f} reasons={verdict.reasons}"
    )

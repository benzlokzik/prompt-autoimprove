from prompt_autoimprove.core.complexity import classify
from prompt_autoimprove.core.normalizer import normalize
from prompt_autoimprove.domain.prompt import Prompt


def _classify(text: str):
    return classify(normalize(Prompt(text=text)))


def test_short_chat_is_simple() -> None:
    verdict = _classify("translate hello to French")
    assert verdict.label == "simple"
    assert verdict.score < 0.5


def test_long_prompt_escalates() -> None:
    verdict = _classify("Please review this design. " * 40)
    assert verdict.label == "hard"
    assert "long_text" in " ".join(verdict.reasons)


def test_reasoning_task_escalates() -> None:
    verdict = _classify(
        "Prove step by step that the algorithm terminates and explain the invariant "
        "you rely on, then justify the worst-case complexity."
    )
    assert verdict.label == "hard"


def test_unfilled_params_contribute() -> None:
    verdict = _classify(
        "Write code that does {thing} for {user} when {condition} holds. " "Step by step please."
    )
    assert verdict.label == "hard"
    assert any(r.startswith("unfilled_params") for r in verdict.reasons)

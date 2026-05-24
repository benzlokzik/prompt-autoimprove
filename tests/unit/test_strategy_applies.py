from prompt_autoimprove.core.strategies.structured_output import StructuredOutputStrategy
from prompt_autoimprove.domain.prompt import NormalizedPrompt, Prompt
from prompt_autoimprove.domain.task_type import TaskType


def _norm(task: str) -> NormalizedPrompt:
    return NormalizedPrompt(
        source=Prompt(text="x"),
        cleaned_text="x",
        detected_language="en",
        detected_task=task,
        missing_parameters=(),
        safety_flags=(),
    )


def test_structured_output_applies_for_formatted_task() -> None:
    strategy = StructuredOutputStrategy()
    assert strategy.applies(_norm(TaskType.EXTRACT.value), None) is True  # type: ignore[arg-type]


def test_structured_output_skips_unformatted_task() -> None:
    strategy = StructuredOutputStrategy()
    assert strategy.applies(_norm(TaskType.REASONING.value), None) is False  # type: ignore[arg-type]

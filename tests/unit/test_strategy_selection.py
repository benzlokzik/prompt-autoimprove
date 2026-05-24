from prompt_autoimprove.core.strategy_selector import (
    _PRIORITY,
    _REASONING_PRIORITY,
    _priority_for,
    select,
)
from prompt_autoimprove.domain.model_profile import ModelFamily, ModelFormat, ModelProfile
from prompt_autoimprove.domain.prompt import NormalizedPrompt, Prompt
from prompt_autoimprove.domain.strategy import StrategyName
from prompt_autoimprove.domain.task_type import TaskType


def _profile() -> ModelProfile:
    return ModelProfile(
        name="qwen3-test",
        family=ModelFamily.QWEN,
        format=ModelFormat.GGUF,
        context_window=8192,
        max_output_tokens=1024,
    )


def _normalized(task: str) -> NormalizedPrompt:
    text = "Please handle this multi-step request with enough detail to be realistic."
    return NormalizedPrompt(
        source=Prompt(text=text),
        cleaned_text=text,
        detected_language="en",
        detected_task=task,
        missing_parameters=(),
        safety_flags=(),
    )


def test_priority_table_depends_on_task() -> None:
    assert _priority_for(TaskType.CODE_GENERATE.value) is _REASONING_PRIORITY
    assert _priority_for(TaskType.REASONING.value) is _REASONING_PRIORITY
    assert _priority_for(TaskType.QA.value) is _PRIORITY


def test_reasoning_task_floats_decomposition_before_role() -> None:
    names = [s.name for s in select(_normalized(TaskType.CODE_GENERATE.value), _profile())]
    assert StrategyName.CHAIN_DECOMPOSITION in names
    assert StrategyName.ROLE_BASED in names
    assert names.index(StrategyName.CHAIN_DECOMPOSITION) < names.index(StrategyName.ROLE_BASED)


def test_default_task_keeps_role_based_first() -> None:
    names = [s.name for s in select(_normalized(TaskType.QA.value), _profile())]
    assert names[0] is StrategyName.ROLE_BASED


def test_select_respects_limit() -> None:
    result = select(_normalized(TaskType.CODE_GENERATE.value), _profile(), limit=2)
    assert len(result) == 2

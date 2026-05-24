from hypothesis import given
from hypothesis import strategies as st

from prompt_autoimprove.core.evaluator import DEFAULT_WEIGHTS, IntegratedScorer, resolve_weights
from prompt_autoimprove.domain.evaluation import MetricName
from prompt_autoimprove.domain.model_profile import ModelFamily, ModelFormat, ModelProfile
from prompt_autoimprove.domain.task_type import TaskType


def _profile(fmt: ModelFormat) -> ModelProfile:
    return ModelProfile(
        name="p",
        family=ModelFamily.QWEN,
        format=fmt,
        context_window=4096,
        max_output_tokens=1024,
    )


def _normalized(base: dict[MetricName, float]) -> dict[MetricName, float]:
    total = sum(base.values())
    return {k: v / total for k, v in base.items()}


def test_local_profile_emphasizes_cost_and_latency() -> None:
    base = _normalized(DEFAULT_WEIGHTS)
    local = _normalized(resolve_weights(DEFAULT_WEIGHTS, _profile(ModelFormat.GGUF), task=None))
    assert local[MetricName.TOKEN_COST] > base[MetricName.TOKEN_COST]
    assert local[MetricName.LATENCY] > base[MetricName.LATENCY]


def test_api_profile_default_task_keeps_base_weights() -> None:
    resolved = resolve_weights(DEFAULT_WEIGHTS, _profile(ModelFormat.API), task=TaskType.QA.value)
    assert resolved == DEFAULT_WEIGHTS


def test_reasoning_task_emphasizes_clarity_and_compliance() -> None:
    base = _normalized(DEFAULT_WEIGHTS)
    api = _profile(ModelFormat.API)
    reasoning = _normalized(
        resolve_weights(DEFAULT_WEIGHTS, api, task=TaskType.CODE_GENERATE.value)
    )
    assert reasoning[MetricName.CLARITY] > base[MetricName.CLARITY]
    assert reasoning[MetricName.PROMPT_COMPLIANCE] > base[MetricName.PROMPT_COMPLIANCE]


@given(
    fmt=st.sampled_from(list(ModelFormat)),
    task=st.sampled_from([t.value for t in TaskType] + [None]),
)
def test_resolved_weights_normalize_and_stay_positive(fmt: ModelFormat, task: str | None) -> None:
    scorer = IntegratedScorer(profile_aware=True)
    weights = scorer._weights_for(_profile(fmt), task)
    assert abs(sum(weights.values()) - 1.0) < 1e-9
    assert all(w > 0.0 for w in weights.values())
    assert set(weights) == set(MetricName)

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass

import pytest

from prompt_autoimprove.adapters.base import (
    AdapterUnavailable,
    GenerationRequest,
    GenerationResult,
)
from prompt_autoimprove.adapters.circuit_breaker import (
    BreakerState,
    CircuitBreakerAdapter,
    CircuitOpenError,
)
from prompt_autoimprove.domain.model_profile import ModelFamily, ModelFormat, ModelProfile


def _profile() -> ModelProfile:
    return ModelProfile(
        name="t",
        family=ModelFamily.OTHER,
        format=ModelFormat.API,
        context_window=1024,
        max_output_tokens=128,
    )


@dataclass(slots=True)
class _FailingAdapter:
    profile: ModelProfile
    name: str = "failing"
    fail_times: int = 99
    calls: int = 0

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise AdapterUnavailable("nope")
        return GenerationResult(text="ok", input_tokens=1, output_tokens=1)

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        yield "x"


@pytest.mark.asyncio
async def test_breaker_opens_after_threshold() -> None:
    inner = _FailingAdapter(profile=_profile())
    breaker = CircuitBreakerAdapter(inner=inner, failure_threshold=3)
    for _ in range(3):
        with pytest.raises(AdapterUnavailable):
            await breaker.generate(GenerationRequest(prompt="x"))
    assert breaker.state is BreakerState.OPEN
    with pytest.raises(CircuitOpenError):
        await breaker.generate(GenerationRequest(prompt="x"))


@pytest.mark.asyncio
async def test_breaker_half_open_recovers() -> None:
    inner = _FailingAdapter(profile=_profile(), fail_times=2)
    breaker = CircuitBreakerAdapter(inner=inner, failure_threshold=2, reset_after_seconds=0.05)
    for _ in range(2):
        with pytest.raises(AdapterUnavailable):
            await breaker.generate(GenerationRequest(prompt="x"))
    assert breaker.state is BreakerState.OPEN
    await asyncio.sleep(0.06)
    result = await breaker.generate(GenerationRequest(prompt="x"))
    assert result.text == "ok"
    assert breaker.state is BreakerState.CLOSED

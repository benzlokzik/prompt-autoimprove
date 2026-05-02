import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import StrEnum

from prompt_autoimprove.adapters.base import (
    AdapterError,
    AdapterUnavailable,
    GenerationRequest,
    GenerationResult,
    ModelAdapter,
)
from prompt_autoimprove.domain.model_profile import ModelProfile


class BreakerState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(AdapterUnavailable):
    pass


@dataclass(slots=True)
class CircuitBreakerAdapter:
    inner: ModelAdapter
    failure_threshold: int = 3
    reset_after_seconds: float = 30.0
    name: str = "circuit-breaker"
    state: BreakerState = BreakerState.CLOSED
    _failures: int = 0
    _opened_at: float = field(default=0.0, repr=False)

    @property
    def profile(self) -> ModelProfile:
        return self.inner.profile

    def _allow(self) -> bool:
        if self.state is BreakerState.CLOSED:
            return True
        elapsed = time.monotonic() - self._opened_at
        if elapsed >= self.reset_after_seconds:
            self.state = BreakerState.HALF_OPEN
            return True
        return False

    def _record_success(self) -> None:
        self._failures = 0
        self.state = BreakerState.CLOSED

    def _record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self.state = BreakerState.OPEN
            self._opened_at = time.monotonic()

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if not self._allow():
            raise CircuitOpenError(f"breaker open for adapter {self.inner.name}")
        try:
            result = await self.inner.generate(request)
        except AdapterError:
            self._record_failure()
            raise
        self._record_success()
        return result

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        if not self._allow():
            raise CircuitOpenError(f"breaker open for adapter {self.inner.name}")
        try:
            async for chunk in self.inner.stream(request):
                yield chunk
        except AdapterError:
            self._record_failure()
            raise
        self._record_success()

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from prompt_autoimprove.domain.model_profile import ModelProfile


@dataclass(slots=True, frozen=True)
class GenerationRequest:
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.2
    top_p: float = 0.95
    stop: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class GenerationResult:
    text: str
    input_tokens: int
    output_tokens: int
    finish_reason: str = "stop"


@runtime_checkable
class ModelAdapter(Protocol):
    name: str
    profile: ModelProfile

    async def generate(self, request: GenerationRequest) -> GenerationResult: ...

    def stream(self, request: GenerationRequest) -> AsyncIterator[str]: ...


class AdapterError(RuntimeError):
    pass


class AdapterUnavailable(AdapterError):
    pass

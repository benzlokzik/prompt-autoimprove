"""Model profile: capabilities and constraints of a target LLM."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ModelFamily(StrEnum):
    QWEN = "qwen"
    LLAMA = "llama"
    GEMMA = "gemma"
    MISTRAL = "mistral"
    OTHER = "other"


class ModelFormat(StrEnum):
    GGUF = "gguf"
    SAFETENSORS = "safetensors"
    API = "api"


class ReasoningMode(StrEnum):
    NONE = "none"
    THINKING = "thinking"
    HYBRID = "hybrid"


@dataclass(slots=True, frozen=True)
class ModelProfile:
    """Static capabilities of a target model."""

    name: str
    family: ModelFamily
    format: ModelFormat
    context_window: int
    max_output_tokens: int
    supports_vision: bool = False
    supports_tools: bool = False
    reasoning_mode: ReasoningMode = ReasoningMode.NONE
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    p50_latency_ms: int = 0
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_local(self) -> bool:
        return self.format in (ModelFormat.GGUF, ModelFormat.SAFETENSORS)

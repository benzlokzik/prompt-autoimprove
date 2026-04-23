from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from prompt_autoimprove.adapters.base import (
    AdapterUnavailable,
    GenerationRequest,
    GenerationResult,
)
from prompt_autoimprove.domain.model_profile import ModelProfile


@dataclass(slots=True)
class SafetensorsHFAdapter:
    profile: ModelProfile
    model_id: str
    device: str = "auto"
    dtype: str = "auto"
    name: str = "safetensors-hf"
    _pipeline: Any = field(default=None, repr=False)

    def _load(self) -> Any:
        if self._pipeline is not None:
            return self._pipeline
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise AdapterUnavailable("transformers is not installed") from exc
        self._pipeline = pipeline(
            "text-generation",
            model=self.model_id,
            device_map=self.device,
            torch_dtype=self.dtype,
        )
        return self._pipeline

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        pipe = self._load()
        out = pipe(
            request.prompt,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            do_sample=request.temperature > 0,
            return_full_text=False,
        )
        text = out[0]["generated_text"] if out else ""
        return GenerationResult(
            text=text,
            input_tokens=len(request.prompt) // 4,
            output_tokens=len(text) // 4,
        )

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        result = await self.generate(request)
        yield result.text

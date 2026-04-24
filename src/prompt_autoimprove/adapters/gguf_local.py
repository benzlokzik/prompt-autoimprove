from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from prompt_autoimprove.adapters.base import (
    AdapterUnavailable,
    GenerationRequest,
    GenerationResult,
)
from prompt_autoimprove.domain.model_profile import ModelProfile


@dataclass(slots=True)
class GGUFAdapter:
    profile: ModelProfile
    model_path: Path
    n_ctx: int = 4096
    n_gpu_layers: int = 0
    name: str = "gguf-local"
    _llm: Any = field(default=None, repr=False)

    def _load(self) -> Any:
        if self._llm is not None:
            return self._llm
        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise AdapterUnavailable("llama-cpp-python is not installed") from exc
        if not self.model_path.exists():
            raise AdapterUnavailable(f"model file not found: {self.model_path}")
        self._llm = Llama(
            model_path=str(self.model_path),
            n_ctx=self.n_ctx,
            n_gpu_layers=self.n_gpu_layers,
            verbose=False,
        )
        return self._llm

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        llm = self._load()
        result = llm.create_completion(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop=list(request.stop) or None,
        )
        choice = result["choices"][0]
        usage = result.get("usage", {})
        return GenerationResult(
            text=choice["text"],
            input_tokens=int(usage.get("prompt_tokens", 0)),
            output_tokens=int(usage.get("completion_tokens", 0)),
            finish_reason=str(choice.get("finish_reason", "stop")),
        )

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        llm = self._load()
        for chunk in llm.create_completion(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop=list(request.stop) or None,
            stream=True,
        ):
            piece = chunk["choices"][0]["text"]
            if piece:
                yield piece

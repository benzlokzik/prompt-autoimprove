from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx

from prompt_autoimprove.adapters._attachments import to_openai_blocks
from prompt_autoimprove.adapters.base import (
    AdapterError,
    AdapterUnavailable,
    GenerationRequest,
    GenerationResult,
)
from prompt_autoimprove.domain.model_profile import ModelProfile


@dataclass(slots=True)
class OpenAICompatAdapter:
    profile: ModelProfile
    base_url: str
    model: str
    api_key: str = ""
    timeout: float = 60.0
    name: str = "openai-compat"

    def _headers(self) -> dict[str, str]:
        h = {"content-type": "application/json"}
        if self.api_key:
            h["authorization"] = f"Bearer {self.api_key}"
        return h

    def _endpoint(self) -> str:
        base = self.base_url.rstrip("/")
        if not base.endswith("/v1"):
            base = f"{base}/v1"
        return f"{base}/chat/completions"

    def _content(self, request: GenerationRequest) -> str | list[dict[str, object]]:
        if not request.attachments or not self.profile.supports_vision:
            return request.prompt
        image_blocks = to_openai_blocks(request.attachments)
        if not image_blocks:
            return request.prompt
        return [{"type": "text", "text": request.prompt}, *image_blocks]

    def _payload(self, request: GenerationRequest, *, stream: bool) -> dict[str, object]:
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": self._content(request)}],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stop": list(request.stop) if request.stop else None,
            "stream": stream,
        }

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    self._endpoint(),
                    headers=self._headers(),
                    json=self._payload(request, stream=False),
                )
            except httpx.HTTPError as exc:
                raise AdapterUnavailable(str(exc)) from exc
        if resp.status_code >= 500:
            raise AdapterUnavailable(f"upstream {resp.status_code}: {resp.text}")
        if resp.status_code >= 400:
            raise AdapterError(f"upstream {resp.status_code}: {resp.text}")
        data = resp.json()
        choice = data["choices"][0]
        usage = data.get("usage", {})
        return GenerationResult(
            text=choice["message"]["content"],
            input_tokens=int(usage.get("prompt_tokens", 0)),
            output_tokens=int(usage.get("completion_tokens", 0)),
            finish_reason=str(choice.get("finish_reason", "stop")),
        )

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        async with (
            httpx.AsyncClient(timeout=self.timeout) as client,
            client.stream(
                "POST",
                self._endpoint(),
                headers=self._headers(),
                json=self._payload(request, stream=True),
            ) as resp,
        ):
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line.removeprefix("data:").strip()
                if payload == "[DONE]":
                    return
                yield payload

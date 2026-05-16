from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx

from prompt_autoimprove.adapters._attachments import to_anthropic_blocks
from prompt_autoimprove.adapters.base import (
    AdapterError,
    AdapterUnavailable,
    GenerationRequest,
    GenerationResult,
)
from prompt_autoimprove.domain.model_profile import ModelProfile

_DEFAULT_VERSION = "2023-06-01"


@dataclass(slots=True)
class AnthropicAdapter:
    profile: ModelProfile
    model: str
    api_key: str
    base_url: str = "https://api.anthropic.com"
    timeout: float = 60.0
    name: str = "anthropic"

    def _headers(self, *, stream: bool) -> dict[str, str]:
        h = {
            "x-api-key": self.api_key,
            "anthropic-version": _DEFAULT_VERSION,
            "content-type": "application/json",
        }
        if stream:
            h["accept"] = "text/event-stream"
        return h

    def _content(self, request: GenerationRequest) -> str | list[dict[str, object]]:
        if not request.attachments or not self.profile.supports_vision:
            return request.prompt
        image_blocks = to_anthropic_blocks(request.attachments)
        if not image_blocks:
            return request.prompt
        return [*image_blocks, {"type": "text", "text": request.prompt}]

    def _payload(self, request: GenerationRequest, *, stream: bool) -> dict[str, object]:
        return {
            "model": self.model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stop_sequences": list(request.stop) or None,
            "stream": stream,
            "messages": [{"role": "user", "content": self._content(request)}],
        }

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    f"{self.base_url.rstrip('/')}/v1/messages",
                    headers=self._headers(stream=False),
                    json=self._payload(request, stream=False),
                )
            except httpx.HTTPError as exc:
                raise AdapterUnavailable(str(exc)) from exc
        if resp.status_code >= 500:
            raise AdapterUnavailable(f"upstream {resp.status_code}: {resp.text}")
        if resp.status_code >= 400:
            raise AdapterError(f"upstream {resp.status_code}: {resp.text}")
        data = resp.json()
        content_blocks = data.get("content", [])
        text = "".join(
            block.get("text", "") for block in content_blocks if block.get("type") == "text"
        )
        usage = data.get("usage", {})
        return GenerationResult(
            text=text,
            input_tokens=int(usage.get("input_tokens", 0)),
            output_tokens=int(usage.get("output_tokens", 0)),
            finish_reason=str(data.get("stop_reason", "stop")),
        )

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        async with (
            httpx.AsyncClient(timeout=self.timeout) as client,
            client.stream(
                "POST",
                f"{self.base_url.rstrip('/')}/v1/messages",
                headers=self._headers(stream=True),
                json=self._payload(request, stream=True),
            ) as resp,
        ):
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line.removeprefix("data:").strip()
                if not payload or payload == "[DONE]":
                    continue
                yield payload

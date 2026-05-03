import json
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(slots=True)
class BackendClient:
    base_url: str
    api_key: str
    timeout: float = 60.0

    @classmethod
    def from_env(cls) -> "BackendClient":
        return cls(
            base_url=os.environ.get("PAI_BACKEND_URL", "http://localhost:8000").rstrip("/"),
            api_key=os.environ.get("PAI_API_KEY", "dev-key"),
        )

    def _headers(self) -> dict[str, str]:
        return {"x-api-key": self.api_key, "content-type": "application/json"}

    async def list_profiles(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/v1/profiles", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def history(self, session_ref: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.base_url}/v1/history/{session_ref}", headers=self._headers()
            )
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            return resp.json()

    async def stream_improve(
        self,
        prompt: str,
        profile: str,
        *,
        locale_hint: str | None = None,
    ) -> AsyncIterator[tuple[str, dict[str, Any]]]:
        params: dict[str, str] = {"prompt": prompt, "profile": profile}
        if locale_hint:
            params["locale_hint"] = locale_hint
        headers = {"x-api-key": self.api_key, "accept": "text/event-stream"}
        async with (
            httpx.AsyncClient(timeout=self.timeout) as client,
            client.stream(
                "GET",
                f"{self.base_url}/v1/improve/stream",
                headers=headers,
                params=params,
            ) as resp,
        ):
            resp.raise_for_status()
            event: str | None = None
            async for line in resp.aiter_lines():
                if line.startswith("event:"):
                    event = line.removeprefix("event:").strip()
                elif line.startswith("data:") and event:
                    payload = json.loads(line.removeprefix("data:").strip())
                    yield event, payload
                    event = None

    async def improve(
        self,
        prompt: str,
        profile: str,
        *,
        session_ref: str | None = None,
        sensitive: bool = False,
        locale_hint: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "prompt": prompt,
            "profile": profile,
            "sensitive": sensitive,
        }
        if session_ref:
            body["session_ref"] = session_ref
        if locale_hint:
            body["locale_hint"] = locale_hint
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/v1/improve", headers=self._headers(), json=body
            )
            resp.raise_for_status()
            return resp.json()

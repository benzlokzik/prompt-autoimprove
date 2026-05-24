import json
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

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
                f"{self.base_url}/v1/history/{quote(session_ref, safe='')}",
                headers=self._headers(),
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
        sensitive: bool = False,
        attachments: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[tuple[str, dict[str, Any]]]:
        # Mirror the inputs of the follow-up improve() call so the streamed
        # preview matches the final result (and sensitive content stays local).
        body: dict[str, Any] = {"prompt": prompt, "profile": profile, "sensitive": sensitive}
        if locale_hint:
            body["locale_hint"] = locale_hint
        if attachments:
            body["attachments"] = attachments
        headers = {
            "x-api-key": self.api_key,
            "accept": "text/event-stream",
            "content-type": "application/json",
        }
        # No read timeout: gaps between SSE events (e.g. a slow probation run)
        # must not abort the stream.
        timeout = httpx.Timeout(connect=10.0, read=None, write=10.0, pool=10.0)
        async with (
            httpx.AsyncClient(timeout=timeout) as client,
            client.stream(
                "POST",
                f"{self.base_url}/v1/improve/stream",
                headers=headers,
                json=body,
            ) as resp,
        ):
            resp.raise_for_status()
            event: str | None = None
            data_lines: list[str] = []
            async for line in resp.aiter_lines():
                if line.startswith("event:"):
                    event = line.removeprefix("event:").strip()
                elif line.startswith("data:"):
                    data_lines.append(line.removeprefix("data:").strip())
                elif line == "" and event and data_lines:
                    try:
                        payload = json.loads("\n".join(data_lines))
                    except json.JSONDecodeError:
                        payload = None
                    if payload is not None:
                        yield event, payload
                    event, data_lines = None, []

    async def improve(
        self,
        prompt: str,
        profile: str,
        *,
        session_ref: str | None = None,
        sensitive: bool = False,
        locale_hint: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
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
        if attachments:
            body["attachments"] = attachments
        # The full pipeline (incl. a model probation run) can take a while.
        timeout = httpx.Timeout(self.timeout, read=300.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{self.base_url}/v1/improve", headers=self._headers(), json=body
            )
            resp.raise_for_status()
            return resp.json()

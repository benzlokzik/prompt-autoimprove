import httpx
import pytest


@pytest.mark.asyncio
async def test_healthz_reports_ready(client: httpx.AsyncClient) -> None:
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"status": "ok", "orchestrator": True, "persistence": True}


@pytest.mark.asyncio
async def test_healthz_requires_no_api_key(client: httpx.AsyncClient) -> None:
    # Probe must be reachable without auth for Docker/orchestrator checks.
    resp = await client.get("/healthz")
    assert resp.status_code == 200

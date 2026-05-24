import httpx
import pytest


@pytest.mark.asyncio
async def test_improve_requires_api_key(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/v1/improve", json={"prompt": "Summarize this", "profile": "qwen3-7b"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_improve_persists_and_history_returns_it(client: httpx.AsyncClient) -> None:
    headers = {"x-api-key": "test-key"}
    resp = await client.post(
        "/v1/improve",
        headers=headers,
        json={
            "prompt": "Summarize this article about microservices",
            "profile": "qwen3-7b",
            "session_ref": "user-42",
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["strategy"]
    assert body["score"] > 0
    assert body["session_id"]

    history = await client.get("/v1/history/user-42", headers=headers)
    assert history.status_code == 200
    items = history.json()
    assert len(items) == 1
    assert items[0]["text"] == "Summarize this article about microservices"
    assert items[0]["revisions"]
    assert items[0]["revisions"][0]["strategy"] == body["strategy"]


@pytest.mark.asyncio
async def test_unknown_profile_returns_404(client: httpx.AsyncClient) -> None:
    headers = {"x-api-key": "test-key"}
    resp = await client.post(
        "/v1/improve",
        headers=headers,
        json={"prompt": "hi", "profile": "no-such-profile"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_improve_accepts_image_attachment(client: httpx.AsyncClient) -> None:
    headers = {"x-api-key": "test-key"}
    data_uri = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
        "YPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    )
    resp = await client.post(
        "/v1/improve",
        headers=headers,
        json={
            "prompt": "Describe what is in this image.",
            "profile": "gemma-4-e2b",
            "attachments": [
                {"modality": "image", "uri": data_uri, "mime_type": "image/png", "bytes_size": 68}
            ],
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["strategy"]
    # The base64 blob must not leak into the candidate prompt text.
    assert "base64," not in body["candidate"]


@pytest.mark.asyncio
async def test_rate_limit_kicks_in(client: httpx.AsyncClient) -> None:
    headers = {"x-api-key": "test-key"}
    body = {"prompt": "Summarize", "profile": "qwen3-7b"}
    statuses = []
    for _ in range(5):
        resp = await client.post("/v1/improve", headers=headers, json=body)
        statuses.append(resp.status_code)
    assert 429 in statuses, f"expected at least one 429, got {statuses}"

import httpx
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from prompt_autoimprove.api.http.app import create_app
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.persistence.models import Base
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator


@pytest.fixture
async def app(profiles, monkeypatch):
    monkeypatch.setenv("PAI_API__API_KEY", "test-key")
    monkeypatch.setenv("PAI_API__RATE_LIMIT_PER_MINUTE", "3")
    from prompt_autoimprove.api.http.rate_limit import limiter
    from prompt_autoimprove.config import get_settings

    get_settings.cache_clear()
    limiter.reset()

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sm = async_sessionmaker(engine, expire_on_commit=False)

    adapters: dict = {}
    orchestrator = AutoImproveOrchestrator(
        profiles=profiles,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=EventPublisher(),
        session_factory=sm,
    )
    application = create_app()
    application.state.orchestrator = orchestrator
    application.state.profiles = profiles
    application.state.session_factory = sm
    yield application
    await engine.dispose()


@pytest.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


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
async def test_rate_limit_kicks_in(client: httpx.AsyncClient) -> None:
    headers = {"x-api-key": "test-key"}
    body = {"prompt": "Summarize", "profile": "qwen3-7b"}
    statuses = []
    for _ in range(5):
        resp = await client.post("/v1/improve", headers=headers, json=body)
        statuses.append(resp.status_code)
    assert 429 in statuses, f"expected at least one 429, got {statuses}"

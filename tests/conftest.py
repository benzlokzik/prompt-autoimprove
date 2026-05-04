from pathlib import Path

import httpx
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from prompt_autoimprove.api.http.app import create_app
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.persistence.models import Base
from prompt_autoimprove.registry.loader import load_profiles
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator

PROFILES_DIR = Path(__file__).resolve().parents[1] / "src/prompt_autoimprove/registry/profiles"


@pytest.fixture
def profiles() -> dict:
    return load_profiles(PROFILES_DIR)


@pytest.fixture
def orchestrator(profiles: dict) -> AutoImproveOrchestrator:
    adapters: dict = {}
    return AutoImproveOrchestrator(
        profiles=profiles,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=EventPublisher(),
    )


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
    pipeline = AutoImproveOrchestrator(
        profiles=profiles,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=EventPublisher(),
        session_factory=sm,
    )
    application = create_app()
    application.state.orchestrator = pipeline
    application.state.profiles = profiles
    application.state.session_factory = sm
    yield application
    await engine.dispose()


@pytest.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

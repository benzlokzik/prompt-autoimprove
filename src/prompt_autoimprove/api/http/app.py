from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from prompt_autoimprove.adapters.factory import build_adapters_from_env
from prompt_autoimprove.api.http.routes import history, improve, profiles
from prompt_autoimprove.config import get_settings
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.logging import configure_logging, get_logger
from prompt_autoimprove.persistence.models import Base
from prompt_autoimprove.registry.loader import load_profiles
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator

logger = get_logger(__name__)


async def _maybe_create_session_factory(dsn: str) -> async_sessionmaker | None:
    try:
        engine = create_async_engine(dsn, echo=False, future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return async_sessionmaker(engine, expire_on_commit=False)
    except Exception as exc:
        logger.warning("persistence.unavailable", error=str(exc))
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    profiles_map = load_profiles(Path(settings.profiles_dir))
    adapters = build_adapters_from_env(profiles_map)
    publisher = EventPublisher()
    await publisher.start()
    session_factory = await _maybe_create_session_factory(settings.db.dsn)
    orchestrator = AutoImproveOrchestrator(
        profiles=profiles_map,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=publisher,
        session_factory=session_factory,
    )
    app.state.orchestrator = orchestrator
    app.state.profiles = profiles_map
    app.state.session_factory = session_factory
    try:
        yield
    finally:
        await publisher.stop()


def create_app() -> FastAPI:
    app = FastAPI(title="prompt-autoimprove", version="0.1.0", lifespan=lifespan)
    app.include_router(improve.router)
    app.include_router(profiles.router)
    app.include_router(history.router)
    return app


app = create_app()

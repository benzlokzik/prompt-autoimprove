from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from prompt_autoimprove.adapters.base import ModelAdapter
from prompt_autoimprove.api.http.routes import history, improve, profiles
from prompt_autoimprove.config import get_settings
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.logging import configure_logging
from prompt_autoimprove.registry.loader import load_profiles
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    profiles_map = load_profiles(Path(settings.profiles_dir))
    adapters: dict[str, ModelAdapter] = {}
    publisher = EventPublisher()
    await publisher.start()
    orchestrator = AutoImproveOrchestrator(
        profiles=profiles_map,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=publisher,
    )
    app.state.orchestrator = orchestrator
    app.state.profiles = profiles_map
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

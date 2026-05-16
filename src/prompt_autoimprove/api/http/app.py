from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from prompt_autoimprove.adapters.factory import build_adapters_from_env
from prompt_autoimprove.api.http.rate_limit import limiter
from prompt_autoimprove.api.http.routes import history, improve, profiles
from prompt_autoimprove.config import get_settings
from prompt_autoimprove.core.complexity import build_classifier
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.core.strategies.llm_rewrite import LLMRewriter
from prompt_autoimprove.logging import configure_logging, get_logger
from prompt_autoimprove.persistence.models import Base
from prompt_autoimprove.registry.loader import load_profiles, resolve_profile
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

    rewriter: LLMRewriter | None = None
    improver_adapter = None
    if settings.improver.profile is not None:
        improver_adapter = adapters.get(settings.improver.profile)
        if improver_adapter is None:
            try:
                improver_profile = resolve_profile(profiles_map, settings.improver.profile)
                improver_adapter = adapters.get(improver_profile.name)
            except KeyError:
                improver_adapter = None
        if improver_adapter is not None:
            rewriter = LLMRewriter(
                improver=improver_adapter,
                max_output_tokens=settings.improver.max_output_tokens,
            )

    classifier = build_classifier(settings.classifier, improver=improver_adapter)

    orchestrator = AutoImproveOrchestrator(
        profiles=profiles_map,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=publisher,
        session_factory=session_factory,
        rewriter=rewriter,
        classifier=classifier,
    )
    app.state.orchestrator = orchestrator
    app.state.profiles = profiles_map
    app.state.session_factory = session_factory
    try:
        yield
    finally:
        await publisher.stop()


def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:  # noqa: ARG001
    return JSONResponse(
        status_code=429,
        content={"detail": f"rate limit exceeded: {exc.detail}"},
    )


def create_app() -> FastAPI:
    app = FastAPI(title="prompt-autoimprove", version="0.1.0", lifespan=lifespan)
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.include_router(improve.router)
    app.include_router(profiles.router)
    app.include_router(history.router)
    return app


app = create_app()

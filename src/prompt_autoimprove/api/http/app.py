from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from prompt_autoimprove.api.grpc.server import create_grpc_server
from prompt_autoimprove.api.http.rate_limit import limiter
from prompt_autoimprove.api.http.routes import health, history, improve, profiles
from prompt_autoimprove.bootstrap import build_runtime, shutdown_runtime
from prompt_autoimprove.config import get_settings
from prompt_autoimprove.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    ctx = await build_runtime(settings)
    app.state.orchestrator = ctx.orchestrator
    app.state.profiles = ctx.profiles
    app.state.session_factory = ctx.session_factory

    app.state.grpc_server = None
    if settings.api.grpc_enabled:
        app.state.grpc_server = await create_grpc_server(ctx.orchestrator, settings.api.grpc_port)
        logger.info("grpc.started", port=settings.api.grpc_port)
    try:
        yield
    finally:
        if app.state.grpc_server is not None:
            await app.state.grpc_server.stop(grace=5)
        await shutdown_runtime(ctx)


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
        allow_origins=get_settings().api.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.include_router(health.router)
    app.include_router(improve.router)
    app.include_router(profiles.router)
    app.include_router(history.router)
    return app


app = create_app()

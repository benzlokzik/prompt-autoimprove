import asyncio

import grpc

from prompt_autoimprove.api.grpc.service import AutoImproveService
from prompt_autoimprove.bootstrap import build_runtime, shutdown_runtime
from prompt_autoimprove.config import get_settings
from prompt_autoimprove.logging import configure_logging, get_logger
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator

logger = get_logger(__name__)


async def create_grpc_server(orchestrator: AutoImproveOrchestrator, port: int) -> grpc.aio.Server:
    """Build and start a gRPC server bound to ``port``; returns it already serving."""
    import prompt_autoimprove.api.grpc.generated  # noqa: F401

    from autoimprove.v1 import autoimprove_pb2_grpc as grpc_mod  # isort: skip

    server = grpc.aio.server()
    grpc_mod.add_AutoImproveServicer_to_server(AutoImproveService(orchestrator), server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    return server


async def serve() -> None:
    configure_logging()
    settings = get_settings()
    ctx = await build_runtime(settings)
    server = await create_grpc_server(ctx.orchestrator, settings.api.grpc_port)
    logger.info("grpc.serving", port=settings.api.grpc_port)
    try:
        await server.wait_for_termination()
    finally:
        await server.stop(grace=5)
        await shutdown_runtime(ctx)


if __name__ == "__main__":
    asyncio.run(serve())

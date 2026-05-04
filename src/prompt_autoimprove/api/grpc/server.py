import asyncio
from pathlib import Path

import grpc

from prompt_autoimprove.api.grpc.service import AutoImproveService
from prompt_autoimprove.config import get_settings
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.registry.loader import load_profiles
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator


async def serve() -> None:
    settings = get_settings()
    profiles = load_profiles(Path(settings.profiles_dir))
    publisher = EventPublisher()
    await publisher.start()
    adapters: dict = {}
    orchestrator = AutoImproveOrchestrator(
        profiles=profiles,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=publisher,
    )
    service = AutoImproveService(orchestrator=orchestrator)

    import prompt_autoimprove.api.grpc.generated  # noqa: F401

    from autoimprove.v1 import autoimprove_pb2_grpc as grpc_mod  # isort: skip

    server = grpc.aio.server()
    grpc_mod.add_AutoImproveServicer_to_server(service, server)
    server.add_insecure_port(f"[::]:{settings.api.grpc_port}")
    await server.start()
    try:
        await server.wait_for_termination()
    finally:
        await publisher.stop()


if __name__ == "__main__":
    asyncio.run(serve())

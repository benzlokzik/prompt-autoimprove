import grpc
import pytest

import prompt_autoimprove.api.grpc.generated  # noqa: F401

from autoimprove.v1 import autoimprove_pb2 as pb  # isort: skip
from autoimprove.v1 import autoimprove_pb2_grpc as pb_grpc  # isort: skip

from prompt_autoimprove.api.grpc.service import AutoImproveService
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator


@pytest.mark.asyncio
async def test_grpc_stream_end_to_end(orchestrator: AutoImproveOrchestrator) -> None:
    server = grpc.aio.server()
    pb_grpc.add_AutoImproveServicer_to_server(AutoImproveService(orchestrator), server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        async with grpc.aio.insecure_channel(f"127.0.0.1:{port}") as channel:
            stub = pb_grpc.AutoImproveStub(channel)
            request = pb.ImproveRequest(
                prompt="Summarize this article about microservices",
                profile="qwen3-7b",
            )
            stages: list[str] = []
            async for event in stub.Improve(request):
                stages.append(event.stage)
        assert "normalized" in stages
        assert "strategy_selected" in stages
        assert "candidate" in stages
        assert "final_decision" in stages
    finally:
        await server.stop(grace=None)

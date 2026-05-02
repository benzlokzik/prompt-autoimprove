import os
import socket

import pytest

from prompt_autoimprove.adapters.factory import build_adapters_from_env
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.domain.prompt import Prompt
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost:11434")


def _reachable(addr: str) -> bool:
    host, _, port = addr.partition(":")
    try:
        with socket.create_connection((host, int(port or 11434)), timeout=0.5):
            return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(
    not _reachable(OLLAMA_HOST),
    reason=f"ollama not reachable at {OLLAMA_HOST}",
)


@pytest.mark.asyncio
async def test_probation_against_local_ollama(profiles, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_BASE_URL", f"http://{OLLAMA_HOST}/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "ollama")
    monkeypatch.setenv("OPENAI_TARGET_PROFILE", "ollama-qwen-1_5b")
    monkeypatch.setenv("OPENAI_MODEL_NAME", "qwen2.5:1.5b-instruct")

    adapters = build_adapters_from_env(profiles)
    assert "ollama-qwen-1_5b" in adapters

    orchestrator = AutoImproveOrchestrator(
        profiles=profiles,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=EventPublisher(),
    )

    result = await orchestrator.run(
        Prompt(text="Reply with the single word: ok"),
        "ollama-qwen-1_5b",
    )

    assert result.probation is not None, "expected probation output from real model"
    assert result.probation.text.strip()
    assert result.routing.adapter_name == "openai-compat"

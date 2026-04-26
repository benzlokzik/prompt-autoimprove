from pathlib import Path

import pytest

from prompt_autoimprove.core.evaluator import IntegratedScorer
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

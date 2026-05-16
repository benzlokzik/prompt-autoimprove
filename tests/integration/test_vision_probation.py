from collections.abc import AsyncIterator
from dataclasses import dataclass, field

import pytest

from prompt_autoimprove.adapters.base import GenerationRequest, GenerationResult
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.prompt import Modality, Prompt, PromptAttachment
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator


@dataclass(slots=True)
class _RecordingAdapter:
    profile: ModelProfile
    name: str = "recorder"
    last: GenerationRequest | None = None
    calls: list[GenerationRequest] = field(default_factory=list)

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        self.last = request
        self.calls.append(request)
        return GenerationResult(text="ok", input_tokens=1, output_tokens=1)

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        _ = request
        yield "ok"


def _orch(profiles, adapter: _RecordingAdapter) -> AutoImproveOrchestrator:
    adapters = {adapter.profile.name: adapter}
    return AutoImproveOrchestrator(
        profiles=profiles,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=EventPublisher(),
    )


_IMG = PromptAttachment(
    modality=Modality.IMAGE, uri="https://example.com/x.png", mime_type="image/png"
)


@pytest.mark.asyncio
async def test_attachments_forwarded_to_vision_adapter(profiles) -> None:
    adapter = _RecordingAdapter(profile=profiles["gemma-4-e2b"])
    orch = _orch(profiles, adapter)
    await orch.run(
        Prompt(text="describe", modality=Modality.IMAGE, attachments=[_IMG]),
        "gemma-4-e2b",
    )
    assert adapter.last is not None
    assert adapter.last.attachments == (_IMG,)


@pytest.mark.asyncio
async def test_attachments_dropped_for_text_only_profile(profiles) -> None:
    adapter = _RecordingAdapter(profile=profiles["qwen3-7b"])
    orch = _orch(profiles, adapter)
    await orch.run(
        Prompt(text="describe", modality=Modality.IMAGE, attachments=[_IMG]),
        "qwen3-7b",
    )
    assert adapter.last is not None
    assert adapter.last.attachments == ()


@pytest.mark.asyncio
async def test_family_lookup_routes_to_same_family_adapter(profiles) -> None:
    # Adapter wired by name claude-sonnet-4-6; caller asks for "claude" family.
    adapter = _RecordingAdapter(profile=profiles["claude-sonnet-4-6"])
    orch = _orch(profiles, adapter)
    result = await orch.run(Prompt(text="hi"), "claude")
    assert result.routing.profile.name == "claude-sonnet-4-6"
    assert adapter.last is not None  # probation hit the family-matched adapter

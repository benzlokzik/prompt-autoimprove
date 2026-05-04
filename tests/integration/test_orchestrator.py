import pytest

from prompt_autoimprove.domain.prompt import Modality, Prompt, PromptAttachment
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_runs_end_to_end(orchestrator: AutoImproveOrchestrator) -> None:
    result = await orchestrator.run(
        Prompt(text="Summarize this article about microservices"),
        "qwen3-7b",
    )
    assert result.chosen.text
    assert result.score.integrated > 0
    assert result.run.explanation
    assert result.routing.adapter_name == "dry-run"


@pytest.mark.asyncio
async def test_multimodal_strategy_picks_when_supported(
    orchestrator: AutoImproveOrchestrator,
) -> None:
    prompt = Prompt(
        text="Describe what is in this picture",
        modality=Modality.IMAGE,
        attachments=[
            PromptAttachment(modality=Modality.IMAGE, uri="file://x.png", mime_type="image/png")
        ],
    )
    result = await orchestrator.run(prompt, "gemma-4-e2b")
    strategies_used = {c.strategy.value for c in result.candidates}
    assert "multimodal" in strategies_used


@pytest.mark.asyncio
async def test_stream_emits_expected_stages(orchestrator: AutoImproveOrchestrator) -> None:
    stages = []
    async for stage, _ in orchestrator.stream(
        Prompt(text="Translate to French: hello world"), "claude-sonnet-4-6"
    ):
        stages.append(stage)
    assert stages == [
        "normalized",
        "strategy_selected",
        "candidate",
        "evaluated",
        "final_decision",
    ]

import dataclasses

import pytest

from prompt_autoimprove.domain.prompt import Modality, Prompt, PromptAttachment
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator, PipelineError


class _FakeSpam:
    def __init__(self, value: float) -> None:
        self.value = value

    def score(self, text: str) -> float:
        return self.value


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
    assert "normalized" in stages
    assert "complexity_checked" in stages
    assert "strategy_selected" in stages
    assert "candidate" in stages
    assert "evaluated" in stages
    assert "final_decision" in stages
    assert stages.index("normalized") < stages.index("complexity_checked")
    assert stages.index("complexity_checked") < stages.index("strategy_selected")


@pytest.mark.asyncio
async def test_spam_flag_surfaces_for_russian(orchestrator: AutoImproveOrchestrator) -> None:
    moderated = dataclasses.replace(orchestrator, spam_scorer=_FakeSpam(0.93))
    result = await moderated.run(Prompt(text="Купите дешёвые таблетки сейчас"), "qwen3-7b")
    assert "spam:0.9300" in result.normalized.safety_flags


@pytest.mark.asyncio
async def test_spam_block_rejects_above_threshold(orchestrator: AutoImproveOrchestrator) -> None:
    moderated = dataclasses.replace(
        orchestrator, spam_scorer=_FakeSpam(0.95), spam_block=True, spam_threshold=0.8
    )
    with pytest.raises(PipelineError):
        await moderated.run(Prompt(text="Купите дешёвые таблетки сейчас"), "qwen3-7b")


@pytest.mark.asyncio
async def test_no_scorer_leaves_output_unchanged(orchestrator: AutoImproveOrchestrator) -> None:
    result = await orchestrator.run(Prompt(text="Купите дешёвые таблетки сейчас"), "qwen3-7b")
    assert not any(f.startswith("spam:") for f in result.normalized.safety_flags)

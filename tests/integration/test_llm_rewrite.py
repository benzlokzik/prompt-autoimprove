from collections.abc import AsyncIterator
from dataclasses import dataclass, field

import pytest

from prompt_autoimprove.adapters.base import (
    AdapterError,
    GenerationRequest,
    GenerationResult,
)
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.core.strategies.llm_rewrite import LLMRewriter
from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.prompt import Prompt
from prompt_autoimprove.domain.strategy import StrategyName
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator


@dataclass(slots=True)
class _FakeAdapter:
    name: str = "fake-improver"
    profile: ModelProfile | None = None
    canned: str = "ROLE: senior engineer.\n\nTASK: rewritten output."
    calls: list[GenerationRequest] = field(default_factory=list)
    fail: bool = False

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        self.calls.append(request)
        if self.fail:
            raise AdapterError("boom")
        return GenerationResult(
            text=self.canned, input_tokens=10, output_tokens=20, finish_reason="stop"
        )

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        yield self.canned


def _orchestrator(profiles, rewriter: LLMRewriter | None) -> AutoImproveOrchestrator:
    adapters: dict = {}
    return AutoImproveOrchestrator(
        profiles=profiles,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=EventPublisher(),
        rewriter=rewriter,
    )


_HARD_PROMPT = (
    "Please refactor this 600-line module that handles billing reconciliation. "
    "Identify hot paths, propose data structures, and write unit tests. "
    "Step by step explain each change and prove correctness." + " More context. " * 30
)


@pytest.mark.asyncio
async def test_hard_prompt_triggers_llm_rewrite(profiles) -> None:
    adapter = _FakeAdapter()
    orch = _orchestrator(profiles, LLMRewriter(improver=adapter))

    result = await orch.run(Prompt(text=_HARD_PROMPT), "qwen3-7b")

    assert result.complexity is not None
    assert result.complexity.label == "hard"
    assert len(adapter.calls) == 1
    strategies = {c.strategy for c in result.candidates}
    assert StrategyName.LLM_REWRITE in strategies


@pytest.mark.asyncio
async def test_simple_prompt_skips_llm_rewrite(profiles) -> None:
    adapter = _FakeAdapter()
    orch = _orchestrator(profiles, LLMRewriter(improver=adapter))

    result = await orch.run(Prompt(text="Translate to French: hello world"), "qwen3-7b")

    assert result.complexity is not None
    assert result.complexity.label == "simple"
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_no_rewriter_means_no_escalation(profiles) -> None:
    orch = _orchestrator(profiles, rewriter=None)
    result = await orch.run(Prompt(text=_HARD_PROMPT), "qwen3-7b")
    strategies = {c.strategy for c in result.candidates}
    assert StrategyName.LLM_REWRITE not in strategies


@pytest.mark.asyncio
async def test_sensitive_blocks_llm_rewrite(profiles) -> None:
    adapter = _FakeAdapter()
    orch = _orchestrator(profiles, LLMRewriter(improver=adapter))
    await orch.run(Prompt(text=_HARD_PROMPT), "qwen3-7b", sensitive=True)
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_pii_blocks_llm_rewrite(profiles) -> None:
    adapter = _FakeAdapter()
    orch = _orchestrator(profiles, LLMRewriter(improver=adapter))
    prompt = Prompt(
        text=(
            "Reach out to alice@example.com about the audit. Step by step list every "
            "open ticket, prove the SLA, and propose mitigations. " + "More. " * 80
        )
    )
    await orch.run(prompt, "qwen3-7b")
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_adapter_failure_is_swallowed(profiles) -> None:
    adapter = _FakeAdapter(fail=True)
    orch = _orchestrator(profiles, LLMRewriter(improver=adapter))
    result = await orch.run(Prompt(text=_HARD_PROMPT), "qwen3-7b")
    strategies = {c.strategy for c in result.candidates}
    assert StrategyName.LLM_REWRITE not in strategies
    assert result.chosen.text  # pipeline still produced a winner


@pytest.mark.asyncio
async def test_rewrite_is_cached_across_calls(profiles) -> None:
    adapter = _FakeAdapter()
    rewriter = LLMRewriter(improver=adapter)
    orch = _orchestrator(profiles, rewriter)
    await orch.run(Prompt(text=_HARD_PROMPT), "qwen3-7b")
    await orch.run(Prompt(text=_HARD_PROMPT), "qwen3-7b")
    assert len(adapter.calls) == 1

import asyncio
from dataclasses import dataclass

import pytest

from prompt_autoimprove.adapters.base import GenerationRequest, GenerationResult
from prompt_autoimprove.core.complexity import (
    CompositeClassifier,
    HeuristicClassifier,
    classify_async,
)
from prompt_autoimprove.core.ml_complexity import JudgeClassifier
from prompt_autoimprove.core.normalizer import normalize
from prompt_autoimprove.domain.prompt import Prompt


@dataclass(slots=True)
class _FakeJudge:
    label: str = "hard"
    name: str = "fake-judge"
    profile: object = None
    calls: int = 0

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        self.calls += 1
        return GenerationResult(text=self.label, input_tokens=1, output_tokens=1)

    def stream(self, request: GenerationRequest):
        raise NotImplementedError


def _norm(text: str):
    return normalize(Prompt(text=text))


def test_sync_classify_works_outside_event_loop() -> None:
    judge = _FakeJudge(label="hard")
    verdict = JudgeClassifier(judge=judge).classify(_norm("design a distributed scheduler"))
    assert verdict.label == "hard"


def test_sync_classify_does_not_crash_inside_running_loop() -> None:
    judge = _FakeJudge(label="simple")
    clf = JudgeClassifier(judge=judge)

    async def call_in_loop():
        # The orchestrator runs inside a live loop; the sync entry point must still resolve.
        return clf.classify(_norm("translate hello"))

    verdict = asyncio.run(call_in_loop())
    assert verdict.label == "simple"


@pytest.mark.asyncio
async def test_classify_async_awaits_judge_and_caches() -> None:
    judge = _FakeJudge(label="hard")
    clf = JudgeClassifier(judge=judge)
    norm = _norm("prove this theorem step by step")
    first = await clf.classify_async(norm)
    second = await clf.classify_async(norm)
    assert first.label == "hard"
    assert second is first
    assert judge.calls == 1


@pytest.mark.asyncio
async def test_classify_async_helper_dispatches_to_judge_in_composite_band() -> None:
    judge = _FakeJudge(label="hard")
    composite = CompositeClassifier(
        ml=JudgeClassifier(judge=judge), heuristic=HeuristicClassifier(), lo=0.30, hi=0.55
    )

    @dataclass(slots=True)
    class _StubHeuristic:
        name: str = "stub"

        def classify(self, normalized):
            from prompt_autoimprove.core.complexity import ComplexityVerdict

            return ComplexityVerdict(label="simple", score=0.40, reasons=("stub",))

    composite.heuristic = _StubHeuristic()  # type: ignore[assignment]
    verdict = await classify_async(composite, _norm("anything"))
    assert verdict.label == "hard"
    assert judge.calls == 1

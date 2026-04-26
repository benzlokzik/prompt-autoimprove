from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import uuid4

from prompt_autoimprove.adapters.base import ModelAdapter
from prompt_autoimprove.core import explainer
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.core.normalizer import normalize
from prompt_autoimprove.core.strategies.base import CandidatePrompt
from prompt_autoimprove.core.strategy_selector import select
from prompt_autoimprove.core.validator import validate
from prompt_autoimprove.domain.evaluation import EvaluationRun, Score
from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.prompt import NormalizedPrompt, Prompt
from prompt_autoimprove.domain.routing import RoutingDecision
from prompt_autoimprove.domain.strategy import StrategyConfig
from prompt_autoimprove.routing.router import Router
from prompt_autoimprove.services.kafka_producer import EventPublisher, PipelineEvent


@dataclass(slots=True)
class PipelineResult:
    normalized: NormalizedPrompt
    candidates: list[CandidatePrompt]
    chosen: CandidatePrompt
    routing: RoutingDecision
    score: Score
    run: EvaluationRun


@dataclass(slots=True)
class AutoImproveOrchestrator:
    profiles: dict[str, ModelProfile]
    adapters: dict[str, ModelAdapter]
    router: Router
    scorer: IntegratedScorer
    events: EventPublisher
    config: StrategyConfig = StrategyConfig()

    async def run(
        self,
        prompt: Prompt,
        profile_name: str,
        *,
        sensitive: bool = False,
        session_id: str | None = None,
    ) -> PipelineResult:
        sid = session_id or str(uuid4())
        profile = self.profiles[profile_name]

        await self.events.publish(
            PipelineEvent.now("received", sid, {"profile": profile_name})
        )

        normalized = normalize(prompt)
        await self.events.publish(
            PipelineEvent.now(
                "normalized",
                sid,
                {"language": normalized.detected_language, "task": normalized.detected_task},
            )
        )

        strategies = select(normalized, profile)
        candidates = [s.apply(normalized, profile, self.config) for s in strategies]
        if not candidates:
            raise RuntimeError("no strategy produced a candidate")

        scored: list[tuple[CandidatePrompt, Score]] = []
        for cand in candidates:
            report = validate(cand, profile)
            score = self.scorer.score(cand, profile, report)
            scored.append((cand, score))

        chosen, best = max(scored, key=lambda pair: pair[1].integrated)
        runner_ups = [s for c, s in scored if c is not chosen]
        explanation = explainer.explain(chosen, best, runner_ups)

        if self.adapters:
            routing = self.router.pick([profile], chosen.id, sensitive=sensitive)
        else:
            routing = RoutingDecision(
                profile=profile,
                adapter_name="dry-run",
                reason="no adapters configured (improvement-only mode)",
                revision_id=chosen.id,
            )

        run = EvaluationRun(
            revision_id=chosen.id,
            profile_name=profile.name,
            score=best,
            explanation=explanation,
        )

        await self.events.publish(
            PipelineEvent.now(
                "evaluated",
                sid,
                {"strategy": chosen.strategy.value, "score": best.integrated},
            )
        )

        return PipelineResult(
            normalized=normalized,
            candidates=candidates,
            chosen=chosen,
            routing=routing,
            score=best,
            run=run,
        )

    async def stream(
        self, prompt: Prompt, profile_name: str
    ) -> AsyncIterator[tuple[str, dict]]:
        result = await self.run(prompt, profile_name)
        yield "normalized", {
            "language": result.normalized.detected_language,
            "task": result.normalized.detected_task,
        }
        yield "strategy_selected", {"strategy": result.chosen.strategy.value}
        yield "candidate", {"text": result.chosen.text, "rationale": result.chosen.rationale}
        yield "evaluated", {"score": result.score.integrated}
        yield "final_decision", {"explanation": result.run.explanation}

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import async_sessionmaker

from prompt_autoimprove.adapters.base import (
    AdapterError,
    GenerationRequest,
    GenerationResult,
    ModelAdapter,
)
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
from prompt_autoimprove.persistence.repositories import EvaluationRepository, PromptRepository
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
    session_id: UUID
    probation: GenerationResult | None = None


@dataclass(slots=True)
class AutoImproveOrchestrator:
    profiles: dict[str, ModelProfile]
    adapters: dict[str, ModelAdapter]
    router: Router
    scorer: IntegratedScorer
    events: EventPublisher
    config: StrategyConfig = field(default_factory=StrategyConfig)
    session_factory: async_sessionmaker | None = None

    async def run(
        self,
        prompt: Prompt,
        profile_name: str,
        *,
        sensitive: bool = False,
        session_id: str | None = None,
        probation: bool = True,
    ) -> PipelineResult:
        sid_str = session_id or str(uuid4())
        profile = self.profiles[profile_name]

        await self.events.publish(
            PipelineEvent.now("received", sid_str, {"profile": profile_name})
        )

        normalized = normalize(prompt)
        await self.events.publish(
            PipelineEvent.now(
                "normalized",
                sid_str,
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

        probation_result: GenerationResult | None = None
        adapter = self.adapters.get(profile.name)
        if probation and adapter is not None:
            try:
                probation_result = await adapter.generate(
                    GenerationRequest(prompt=chosen.text, max_tokens=profile.max_output_tokens)
                )
            except AdapterError as exc:
                probation_result = None
                await self.events.publish(
                    PipelineEvent.now("probation_failed", sid_str, {"error": str(exc)})
                )

        await self.events.publish(
            PipelineEvent.now(
                "evaluated",
                sid_str,
                {"strategy": chosen.strategy.value, "score": best.integrated},
            )
        )

        sid_uuid = await self._persist(
            sid_str, prompt, chosen, routing, run, best
        )

        return PipelineResult(
            normalized=normalized,
            candidates=candidates,
            chosen=chosen,
            routing=routing,
            score=best,
            run=run,
            session_id=sid_uuid,
            probation=probation_result,
        )

    async def _persist(
        self,
        session_ref: str,
        prompt: Prompt,
        chosen: CandidatePrompt,
        routing: RoutingDecision,
        run: EvaluationRun,
        score: Score,
    ) -> UUID:
        if self.session_factory is None:
            return uuid4()
        async with self.session_factory() as db:
            prompts = PromptRepository(db)
            evals = EvaluationRepository(db)
            session_row = await prompts.create_session(user_ref=session_ref)
            prompt_row = await prompts.add_prompt(
                session_id=session_row.id,
                text=prompt.text,
                modality=prompt.modality.value,
                locale_hint=prompt.locale_hint,
            )
            revision_row = await prompts.add_revision(
                prompt_id=prompt_row.id,
                text=chosen.text,
                strategy=chosen.strategy.value,
                rationale=chosen.rationale,
                estimated_tokens=chosen.estimated_tokens,
            )
            await evals.record(
                revision_id=revision_row.id,
                profile_name=run.profile_name,
                integrated_score=score.integrated,
                explanation=run.explanation,
                metrics=[
                    (m.name.value, m.value, m.raw_value, m.weight) for m in score.metrics
                ],
                routing=(routing.adapter_name, routing.profile.name, routing.reason),
            )
            await db.commit()
            return session_row.id

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
        if result.probation is not None:
            yield "probation", {"output": result.probation.text}
        yield "final_decision", {"explanation": result.run.explanation}

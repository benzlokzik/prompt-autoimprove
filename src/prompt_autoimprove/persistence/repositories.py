from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from prompt_autoimprove.persistence.models import (
    EvaluationMetricRow,
    EvaluationRunRow,
    PromptRevisionRow,
    PromptRow,
    RoutingDecisionRow,
    SessionRow,
)


class PromptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(self, user_ref: str) -> SessionRow:
        row = SessionRow(user_ref=user_ref)
        self.session.add(row)
        await self.session.flush()
        return row

    async def add_prompt(
        self, session_id: UUID, text: str, modality: str, locale_hint: str | None
    ) -> PromptRow:
        row = PromptRow(
            session_id=session_id, text=text, modality=modality, locale_hint=locale_hint
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def add_revision(
        self,
        prompt_id: UUID,
        text: str,
        strategy: str,
        rationale: str,
        estimated_tokens: int,
    ) -> PromptRevisionRow:
        row = PromptRevisionRow(
            prompt_id=prompt_id,
            text=text,
            strategy=strategy,
            rationale=rationale,
            estimated_tokens=estimated_tokens,
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def history(self, session_id: UUID, limit: int = 50) -> Sequence[PromptRow]:
        stmt = (
            select(PromptRow)
            .where(PromptRow.session_id == session_id)
            .order_by(PromptRow.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class EvaluationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(
        self,
        revision_id: UUID,
        profile_name: str,
        integrated_score: float,
        explanation: str,
        metrics: list[tuple[str, float, float, float]],
        routing: tuple[str, str, str],
    ) -> EvaluationRunRow:
        run = EvaluationRunRow(
            revision_id=revision_id,
            profile_name=profile_name,
            integrated_score=integrated_score,
            explanation=explanation,
        )
        self.session.add(run)
        await self.session.flush()
        for name, value, raw, weight in metrics:
            self.session.add(
                EvaluationMetricRow(
                    run_id=run.id, name=name, value=value, raw_value=raw, weight=weight
                )
            )
        adapter_name, profile, reason = routing
        self.session.add(
            RoutingDecisionRow(
                revision_id=revision_id,
                profile_name=profile,
                adapter_name=adapter_name,
                reason=reason,
            )
        )
        return run

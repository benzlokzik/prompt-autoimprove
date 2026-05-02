from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class SessionRow(Base):
    __tablename__ = "sessions"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_ref: Mapped[str] = mapped_column(String(128), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class PromptRow(Base):
    __tablename__ = "prompts"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("sessions.id", ondelete="CASCADE"), index=True
    )
    text: Mapped[str] = mapped_column(Text)
    modality: Mapped[str] = mapped_column(String(16), default="text")
    locale_hint: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    revisions: Mapped[list["PromptRevisionRow"]] = relationship(
        back_populates="prompt", cascade="all, delete-orphan"
    )


class PromptRevisionRow(Base):
    __tablename__ = "prompt_revisions"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    prompt_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("prompts.id", ondelete="CASCADE"), index=True
    )
    parent_revision_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    text: Mapped[str] = mapped_column(Text)
    strategy: Mapped[str] = mapped_column(String(64))
    rationale: Mapped[str] = mapped_column(Text)
    estimated_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    prompt: Mapped[PromptRow] = relationship(back_populates="revisions")


class ModelProfileRow(Base):
    __tablename__ = "model_profiles"
    name: Mapped[str] = mapped_column(String(128), primary_key=True)
    family: Mapped[str] = mapped_column(String(32))
    format: Mapped[str] = mapped_column(String(32))
    context_window: Mapped[int] = mapped_column(Integer)
    max_output_tokens: Mapped[int] = mapped_column(Integer)
    capabilities: Mapped[dict] = mapped_column(JSON, default=dict)
    cost_per_1k_input: Mapped[float] = mapped_column(Float, default=0.0)
    cost_per_1k_output: Mapped[float] = mapped_column(Float, default=0.0)
    p50_latency_ms: Mapped[int] = mapped_column(Integer, default=0)


class RoutingDecisionRow(Base):
    __tablename__ = "routing_decisions"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    revision_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("prompt_revisions.id", ondelete="CASCADE"), index=True
    )
    profile_name: Mapped[str] = mapped_column(String(128))
    adapter_name: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(Text)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class EvaluationRunRow(Base):
    __tablename__ = "evaluation_runs"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    revision_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("prompt_revisions.id", ondelete="CASCADE"), index=True
    )
    profile_name: Mapped[str] = mapped_column(String(128))
    integrated_score: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    metrics: Mapped[list["EvaluationMetricRow"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class EvaluationMetricRow(Base):
    __tablename__ = "evaluation_metrics"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    run_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("evaluation_runs.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(32))
    value: Mapped[float] = mapped_column(Float)
    raw_value: Mapped[float] = mapped_column(Float)
    weight: Mapped[float] = mapped_column(Float)

    run: Mapped[EvaluationRunRow] = relationship(back_populates="metrics")

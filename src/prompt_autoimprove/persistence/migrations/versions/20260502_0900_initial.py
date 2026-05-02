from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260502_0900"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_ref", sa.String(128), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "prompts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("modality", sa.String(16), nullable=False),
        sa.Column("locale_hint", sa.String(16)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "prompt_revisions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "prompt_id",
            sa.Uuid(),
            sa.ForeignKey("prompts.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("parent_revision_id", sa.Uuid()),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("strategy", sa.String(64), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("estimated_tokens", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "model_profiles",
        sa.Column("name", sa.String(128), primary_key=True),
        sa.Column("family", sa.String(32), nullable=False),
        sa.Column("format", sa.String(32), nullable=False),
        sa.Column("context_window", sa.Integer(), nullable=False),
        sa.Column("max_output_tokens", sa.Integer(), nullable=False),
        sa.Column("capabilities", sa.JSON(), nullable=False),
        sa.Column("cost_per_1k_input", sa.Float(), nullable=False),
        sa.Column("cost_per_1k_output", sa.Float(), nullable=False),
        sa.Column("p50_latency_ms", sa.Integer(), nullable=False),
    )
    op.create_table(
        "routing_decisions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "revision_id",
            sa.Uuid(),
            sa.ForeignKey("prompt_revisions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("profile_name", sa.String(128), nullable=False),
        sa.Column("adapter_name", sa.String(64), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "evaluation_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "revision_id",
            sa.Uuid(),
            sa.ForeignKey("prompt_revisions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("profile_name", sa.String(128), nullable=False),
        sa.Column("integrated_score", sa.Float(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "evaluation_metrics",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "run_id",
            sa.Uuid(),
            sa.ForeignKey("evaluation_runs.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(32), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("raw_value", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
    )


def downgrade() -> None:
    for table in (
        "evaluation_metrics",
        "evaluation_runs",
        "routing_decisions",
        "model_profiles",
        "prompt_revisions",
        "prompts",
        "sessions",
    ):
        op.drop_table(table)

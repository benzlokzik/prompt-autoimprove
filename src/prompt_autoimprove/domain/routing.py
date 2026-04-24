from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from prompt_autoimprove.domain.model_profile import ModelProfile


@dataclass(slots=True, frozen=True)
class RoutingDecision:
    """Records which adapter and profile served a candidate."""

    profile: ModelProfile
    adapter_name: str
    reason: str
    revision_id: UUID
    id: UUID = field(default_factory=uuid4)
    decided_at: datetime = field(default_factory=lambda: datetime.now(UTC))

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
from uuid import UUID, uuid4

from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.prompt import NormalizedPrompt
from prompt_autoimprove.domain.strategy import StrategyConfig, StrategyName


@dataclass(slots=True, frozen=True)
class CandidatePrompt:
    """A strategy-produced candidate prompt with provenance."""

    text: str
    strategy: StrategyName
    rationale: str
    estimated_tokens: int
    id: UUID = field(default_factory=uuid4)


@runtime_checkable
class Strategy(Protocol):
    """All strategies expose `name` and `apply`."""

    name: StrategyName

    def applies(self, normalized: NormalizedPrompt, profile: ModelProfile) -> bool: ...

    def apply(
        self,
        normalized: NormalizedPrompt,
        profile: ModelProfile,
        config: StrategyConfig,
    ) -> CandidatePrompt: ...


def estimate_tokens(text: str) -> int:
    """A cheap token estimate: ~4 characters per token plus newlines."""
    return max(1, (len(text) + 3) // 4)

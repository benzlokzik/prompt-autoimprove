from collections.abc import Sequence

from prompt_autoimprove.core.strategies.base import Strategy
from prompt_autoimprove.core.strategies.chain_decomposition import ChainDecompositionStrategy
from prompt_autoimprove.core.strategies.few_shot import FewShotStrategy
from prompt_autoimprove.core.strategies.multimodal import MultimodalStrategy
from prompt_autoimprove.core.strategies.role_based import RoleBasedStrategy
from prompt_autoimprove.core.strategies.self_verification import SelfVerificationStrategy
from prompt_autoimprove.core.strategies.structured_output import StructuredOutputStrategy
from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.prompt import NormalizedPrompt
from prompt_autoimprove.domain.strategy import StrategyName
from prompt_autoimprove.domain.task_type import REASONING_HEAVY

DEFAULT_STRATEGIES: tuple[Strategy, ...] = (
    RoleBasedStrategy(),
    StructuredOutputStrategy(),
    ChainDecompositionStrategy(),
    FewShotStrategy(),
    SelfVerificationStrategy(),
    MultimodalStrategy(),
)

_PRIORITY: dict[StrategyName, int] = {
    StrategyName.MULTIMODAL: 0,
    StrategyName.ROLE_BASED: 1,
    StrategyName.STRUCTURED_OUTPUT: 2,
    StrategyName.CHAIN_DECOMPOSITION: 3,
    StrategyName.FEW_SHOT: 4,
    StrategyName.SELF_VERIFICATION: 5,
}

# Reasoning-heavy tasks decompose and self-check better, so float those ahead of
# the generic role/format strategies while keeping the order deterministic.
_REASONING_PRIORITY: dict[StrategyName, int] = {
    StrategyName.MULTIMODAL: 0,
    StrategyName.CHAIN_DECOMPOSITION: 1,
    StrategyName.SELF_VERIFICATION: 2,
    StrategyName.STRUCTURED_OUTPUT: 3,
    StrategyName.ROLE_BASED: 4,
    StrategyName.FEW_SHOT: 5,
}

_REASONING_TASKS: frozenset[str] = frozenset(t.value for t in REASONING_HEAVY)


def _priority_for(task: str) -> dict[StrategyName, int]:
    return _REASONING_PRIORITY if task in _REASONING_TASKS else _PRIORITY


def select(
    normalized: NormalizedPrompt,
    profile: ModelProfile,
    *,
    pool: Sequence[Strategy] = DEFAULT_STRATEGIES,
    limit: int = 4,
) -> list[Strategy]:
    priority = _priority_for(normalized.detected_task)
    eligible = [s for s in pool if s.applies(normalized, profile)]
    eligible.sort(key=lambda s: priority.get(s.name, 99))
    return eligible[:limit]

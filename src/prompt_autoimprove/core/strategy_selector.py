from __future__ import annotations

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


def select(
    normalized: NormalizedPrompt,
    profile: ModelProfile,
    *,
    pool: Sequence[Strategy] = DEFAULT_STRATEGIES,
    limit: int = 4,
) -> list[Strategy]:
    eligible = [s for s in pool if s.applies(normalized, profile)]
    eligible.sort(key=lambda s: _PRIORITY.get(s.name, 99))
    return eligible[:limit]

from dataclasses import dataclass
from enum import StrEnum


class StrategyName(StrEnum):
    ROLE_BASED = "role_based"
    STRUCTURED_OUTPUT = "structured_output"
    CHAIN_DECOMPOSITION = "chain_decomposition"
    FEW_SHOT = "few_shot"
    SELF_VERIFICATION = "self_verification"
    MULTIMODAL = "multimodal"
    LLM_REWRITE = "llm_rewrite"


@dataclass(slots=True, frozen=True)
class StrategyConfig:
    """Tunable knobs shared across strategies."""

    role: str = "expert assistant"
    output_format: str = "markdown"
    max_examples: int = 2
    enforce_thinking: bool = False
    safety_floor: float = 0.5

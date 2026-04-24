from dataclasses import dataclass

from prompt_autoimprove.core.strategies.base import (
    CandidatePrompt,
    estimate_tokens,
)
from prompt_autoimprove.domain.model_profile import ModelProfile, ReasoningMode
from prompt_autoimprove.domain.prompt import NormalizedPrompt
from prompt_autoimprove.domain.strategy import StrategyConfig, StrategyName
from prompt_autoimprove.domain.task_type import REASONING_HEAVY, TaskType


@dataclass(slots=True)
class ChainDecompositionStrategy:
    name: StrategyName = StrategyName.CHAIN_DECOMPOSITION

    def applies(self, normalized: NormalizedPrompt, profile: ModelProfile) -> bool:
        try:
            task = TaskType(normalized.detected_task)
        except ValueError:
            return False
        if profile.reasoning_mode is ReasoningMode.THINKING:
            return False
        return task in REASONING_HEAVY

    def apply(
        self,
        normalized: NormalizedPrompt,
        profile: ModelProfile,  # noqa: ARG002
        config: StrategyConfig,  # noqa: ARG002
    ) -> CandidatePrompt:
        text = (
            f"{normalized.cleaned_text}\n\n"
            "Solve this in three explicit phases:\n"
            "1. Restate the problem in your own words.\n"
            "2. Plan the solution as a numbered list of sub-steps.\n"
            "3. Execute each sub-step and produce the final answer.\n"
            "Label each phase clearly."
        )
        return CandidatePrompt(
            text=text,
            strategy=self.name,
            rationale="Reasoning-heavy task without native thinking mode — explicit plan added.",
            estimated_tokens=estimate_tokens(text),
        )

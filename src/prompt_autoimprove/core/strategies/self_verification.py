from dataclasses import dataclass

from prompt_autoimprove.core.strategies.base import (
    CandidatePrompt,
    estimate_tokens,
)
from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.prompt import NormalizedPrompt
from prompt_autoimprove.domain.strategy import StrategyConfig, StrategyName

_VERIFICATION_TAIL = (
    "\n\nAfter producing the answer, perform a self-check:\n"
    "- Re-read the user request.\n"
    "- List any constraint you may have missed.\n"
    "- If a constraint was missed, revise the answer accordingly.\n"
    "Return the final, revised answer only."
)


@dataclass(slots=True)
class SelfVerificationStrategy:
    name: StrategyName = StrategyName.SELF_VERIFICATION

    def applies(self, normalized: NormalizedPrompt, profile: ModelProfile) -> bool:
        return profile.max_output_tokens >= 256 and len(normalized.cleaned_text) > 40

    def apply(
        self,
        normalized: NormalizedPrompt,
        profile: ModelProfile,
        config: StrategyConfig,  # noqa: ARG002
    ) -> CandidatePrompt:
        text = normalized.cleaned_text + _VERIFICATION_TAIL
        return CandidatePrompt(
            text=text,
            strategy=self.name,
            rationale="Appended an explicit self-check loop to catch missed constraints.",
            estimated_tokens=estimate_tokens(text, profile.name),
        )

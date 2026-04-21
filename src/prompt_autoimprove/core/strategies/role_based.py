"""Role-based strategy: prepend an explicit expert role and audience."""

from __future__ import annotations

from dataclasses import dataclass

from prompt_autoimprove.core.strategies.base import (
    CandidatePrompt,
    estimate_tokens,
)
from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.prompt import NormalizedPrompt
from prompt_autoimprove.domain.strategy import StrategyConfig, StrategyName
from prompt_autoimprove.domain.task_type import TaskType

_ROLE_BY_TASK: dict[str, str] = {
    TaskType.CODE_GENERATE.value: "senior software engineer",
    TaskType.CODE_EXPLAIN.value: "patient code reviewer",
    TaskType.SUMMARIZE.value: "concise editor",
    TaskType.EXTRACT.value: "meticulous data analyst",
    TaskType.TRANSLATE.value: "professional translator",
    TaskType.REASONING.value: "rigorous logician",
    TaskType.VISION.value: "visual analyst",
}


@dataclass(slots=True)
class RoleBasedStrategy:
    name: StrategyName = StrategyName.ROLE_BASED

    def applies(self, normalized: NormalizedPrompt, profile: ModelProfile) -> bool:  # noqa: ARG002
        return True

    def apply(
        self,
        normalized: NormalizedPrompt,
        profile: ModelProfile,  # noqa: ARG002
        config: StrategyConfig,
    ) -> CandidatePrompt:
        role = _ROLE_BY_TASK.get(normalized.detected_task, config.role)
        text = (
            f"You are a {role}. Answer accurately and stay within scope.\n\n"
            f"User request:\n{normalized.cleaned_text}"
        )
        return CandidatePrompt(
            text=text,
            strategy=self.name,
            rationale=f"Assigned role '{role}' based on task '{normalized.detected_task}'.",
            estimated_tokens=estimate_tokens(text),
        )

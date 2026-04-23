"""Multimodal adaptation: hint the model about attached images or audio."""

from __future__ import annotations

from dataclasses import dataclass

from prompt_autoimprove.core.strategies.base import (
    CandidatePrompt,
    estimate_tokens,
)
from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.prompt import Modality, NormalizedPrompt
from prompt_autoimprove.domain.strategy import StrategyConfig, StrategyName


@dataclass(slots=True)
class MultimodalStrategy:
    name: StrategyName = StrategyName.MULTIMODAL

    def applies(self, normalized: NormalizedPrompt, profile: ModelProfile) -> bool:
        if not profile.supports_vision:
            return False
        prompt = normalized.source
        return prompt.modality is not Modality.TEXT or bool(prompt.attachments)

    def apply(
        self,
        normalized: NormalizedPrompt,
        profile: ModelProfile,  # noqa: ARG002
        config: StrategyConfig,  # noqa: ARG002
    ) -> CandidatePrompt:
        prompt = normalized.source
        attachment_lines = [
            f"- [{att.modality.value}] {att.uri} ({att.mime_type})" for att in prompt.attachments
        ]
        if not attachment_lines:
            attachment_lines = [f"- [{prompt.modality.value}] inline content"]
        attachments_block = "\n".join(attachment_lines)
        text = (
            "You will receive multimodal input. Treat each attachment as authoritative; "
            "describe what you observe before answering.\n\n"
            f"Attachments:\n{attachments_block}\n\n"
            f"Task:\n{normalized.cleaned_text}"
        )
        return CandidatePrompt(
            text=text,
            strategy=self.name,
            rationale=f"Attached {len(attachment_lines)} item(s); model supports vision.",
            estimated_tokens=estimate_tokens(text),
        )

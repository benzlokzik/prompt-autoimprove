from dataclasses import dataclass

from prompt_autoimprove.core.strategies.base import (
    CandidatePrompt,
    estimate_tokens,
)
from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.prompt import NormalizedPrompt
from prompt_autoimprove.domain.strategy import StrategyConfig, StrategyName
from prompt_autoimprove.domain.task_type import TaskType

_FORMAT_BY_TASK: dict[str, str] = {
    TaskType.EXTRACT.value: "json",
    TaskType.CLASSIFY.value: "json",
    TaskType.CODE_GENERATE.value: "fenced-code",
    TaskType.SUMMARIZE.value: "bullet-list",
    TaskType.TRANSLATE.value: "plain",
}

_TEMPLATES: dict[str, str] = {
    "json": (
        "Respond with a single JSON object. No prose before or after. "
        'Schema: {"result": <answer>, "confidence": <0..1>}.'
    ),
    "fenced-code": (
        "Return only one fenced code block in the requested language. "
        "No commentary outside the block."
    ),
    "bullet-list": (
        "Return a markdown bullet list. Each bullet is one short sentence. Avoid headings."
    ),
    "plain": "Return only the translated text, with no quotes and no notes.",
    "markdown": "Format the answer as concise markdown with at most one heading.",
}


@dataclass(slots=True)
class StructuredOutputStrategy:
    name: StrategyName = StrategyName.STRUCTURED_OUTPUT

    def applies(self, normalized: NormalizedPrompt, profile: ModelProfile) -> bool:  # noqa: ARG002
        return normalized.detected_task in _FORMAT_BY_TASK

    def apply(
        self,
        normalized: NormalizedPrompt,
        profile: ModelProfile,  # noqa: ARG002
        config: StrategyConfig,
    ) -> CandidatePrompt:
        fmt = _FORMAT_BY_TASK.get(normalized.detected_task, config.output_format)
        contract = _TEMPLATES.get(fmt, _TEMPLATES["markdown"])
        text = f"{normalized.cleaned_text}\n\nOutput contract: {contract}"
        return CandidatePrompt(
            text=text,
            strategy=self.name,
            rationale=f"Enforced '{fmt}' output for task '{normalized.detected_task}'.",
            estimated_tokens=estimate_tokens(text),
        )

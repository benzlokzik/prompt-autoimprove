"""Few-shot strategy: include task-specific examples when budget permits."""

from __future__ import annotations

from dataclasses import dataclass, field

from prompt_autoimprove.core.strategies.base import (
    CandidatePrompt,
    estimate_tokens,
)
from prompt_autoimprove.domain.model_profile import ModelProfile
from prompt_autoimprove.domain.prompt import NormalizedPrompt
from prompt_autoimprove.domain.strategy import StrategyConfig, StrategyName
from prompt_autoimprove.domain.task_type import TaskType

_DEFAULT_EXAMPLES: dict[str, list[tuple[str, str]]] = {
    TaskType.SUMMARIZE.value: [
        ("Long article about cats…", "- Cats sleep 12-16h.\n- They purr when content."),
        ("Earnings report Q1…", "- Revenue up 12%.\n- Margins flat."),
    ],
    TaskType.CLASSIFY.value: [
        ("'I love this movie!'", '{"result": "positive", "confidence": 0.95}'),
        ("'Worst purchase ever'", '{"result": "negative", "confidence": 0.99}'),
    ],
    TaskType.EXTRACT.value: [
        (
            "Email from Alice on 2025-03-01 about invoice #42.",
            '{"result": {"sender": "Alice", "date": "2025-03-01", "topic": "invoice #42"}, '
            '"confidence": 0.9}',
        ),
    ],
}


@dataclass(slots=True)
class FewShotStrategy:
    name: StrategyName = StrategyName.FEW_SHOT
    examples: dict[str, list[tuple[str, str]]] = field(
        default_factory=lambda: dict(_DEFAULT_EXAMPLES)
    )

    def applies(self, normalized: NormalizedPrompt, profile: ModelProfile) -> bool:
        if normalized.detected_task not in self.examples:
            return False
        budget = profile.context_window - estimate_tokens(normalized.cleaned_text)
        return budget > 256

    def apply(
        self,
        normalized: NormalizedPrompt,
        profile: ModelProfile,
        config: StrategyConfig,
    ) -> CandidatePrompt:
        pool = self.examples.get(normalized.detected_task, [])
        chosen = pool[: max(1, config.max_examples)]
        budget = profile.context_window - estimate_tokens(normalized.cleaned_text) - 64
        rendered: list[str] = []
        used = 0
        for inp, out in chosen:
            block = f"Example input:\n{inp}\nExample output:\n{out}\n"
            cost = estimate_tokens(block)
            if used + cost > budget:
                break
            rendered.append(block)
            used += cost
        body = "\n".join(rendered)
        text = f"{body}\nNow solve:\n{normalized.cleaned_text}"
        return CandidatePrompt(
            text=text,
            strategy=self.name,
            rationale=f"Added {len(rendered)} few-shot example(s) within budget.",
            estimated_tokens=estimate_tokens(text),
        )

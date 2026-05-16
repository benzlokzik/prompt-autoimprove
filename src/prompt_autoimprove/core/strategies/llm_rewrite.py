"""LLM-powered rewrite strategy.

Unlike the six template strategies, this one asks an *improver* model to
produce a rewrite of the user's prompt. It is gated by the complexity
classifier and the presence of an improver adapter, so deployments without
an improver continue to behave exactly as before.

Kept separate from the sync ``Strategy`` protocol because the rewrite needs
to ``await`` the adapter; the orchestrator runs it explicitly.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from prompt_autoimprove.adapters.base import (
    AdapterError,
    GenerationRequest,
    ModelAdapter,
)
from prompt_autoimprove.core.strategies.base import CandidatePrompt, estimate_tokens
from prompt_autoimprove.domain.strategy import StrategyName

if TYPE_CHECKING:
    from prompt_autoimprove.domain.model_profile import ModelProfile
    from prompt_autoimprove.domain.prompt import NormalizedPrompt
    from prompt_autoimprove.domain.strategy import StrategyConfig

_META_PROMPT = """You are a prompt engineer. Rewrite the user's raw request so that a
language model can answer it accurately and concisely.

Apply, as appropriate:
- Assign an expert role.
- Make the task explicit; preserve constraints; remove ambiguity.
- Request a clearly structured output (sections / bullets / JSON if implied).
- Decompose multi-step asks into ordered steps.
- Add one short worked example only if it removes ambiguity.
- Ask the model to self-check before answering.

Do NOT answer the request. Output ONLY the rewritten prompt — no preamble,
no fences, no commentary.

Target model profile: {profile}
Detected task: {task}
Detected language: {language}

--- USER PROMPT START ---
{prompt}
--- USER PROMPT END ---
"""


def _cache_key(text: str, profile_name: str) -> str:
    digest = hashlib.sha256(f"{profile_name}|{text}".encode()).hexdigest()
    return digest[:32]


@dataclass(slots=True)
class LLMRewriter:
    """Calls an improver adapter to produce a single rewritten candidate."""

    improver: ModelAdapter
    max_output_tokens: int = 1024
    _cache: dict[str, CandidatePrompt] = field(default_factory=dict)

    async def rewrite(
        self,
        normalized: NormalizedPrompt,
        profile: ModelProfile,
        config: StrategyConfig,  # noqa: ARG002 — reserved for future tuning
    ) -> CandidatePrompt | None:
        """Return an LLM-rewritten candidate, or ``None`` on adapter failure."""
        key = _cache_key(normalized.cleaned_text, profile.name)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        meta = _META_PROMPT.format(
            profile=profile.name,
            task=normalized.detected_task,
            language=normalized.detected_language,
            prompt=normalized.cleaned_text,
        )

        try:
            result = await self.improver.generate(
                GenerationRequest(prompt=meta, max_tokens=self.max_output_tokens)
            )
        except AdapterError:
            return None

        rewritten = result.text.strip()
        if not rewritten:
            return None

        candidate = CandidatePrompt(
            text=rewritten,
            strategy=StrategyName.LLM_REWRITE,
            rationale=(
                f"LLM rewrite via improver '{self.improver.name}' "
                f"({result.input_tokens}+{result.output_tokens} tokens)."
            ),
            estimated_tokens=estimate_tokens(rewritten),
        )
        self._cache[key] = candidate
        return candidate

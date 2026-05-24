"""Offline scoring benchmark over a fixed prompt set.

Runs normalization, strategy selection, and scoring without any model or
network, and prints the chosen strategy and integrated score with profile-aware
weighting off vs on so algorithm changes can be measured as deltas.

Usage: uv run python scripts/benchmark.py
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.core.normalizer import normalize
from prompt_autoimprove.core.strategy_selector import select
from prompt_autoimprove.core.validator import validate
from prompt_autoimprove.domain.prompt import Prompt
from prompt_autoimprove.domain.strategy import StrategyConfig
from prompt_autoimprove.registry.loader import load_profiles

if TYPE_CHECKING:
    from prompt_autoimprove.domain.model_profile import ModelProfile

_PROFILES_DIR = Path(__file__).resolve().parents[1] / "src/prompt_autoimprove/registry/profiles"

PROMPTS: tuple[str, ...] = (
    "Summarize this article about microservices in a few bullet points.",
    "Extract all email addresses and phone numbers from the text below.",
    "Write a Python function that merges two sorted linked lists.",
    "Translate the following paragraph into French.",
    "Reason step by step: a train leaves at 3pm going 60mph; when does it arrive 150 miles away?",
    "What is the capital of France?",
)


def _pick_profiles(profiles: dict[str, ModelProfile]) -> list[ModelProfile]:
    local = next((p for p in profiles.values() if p.is_local), None)
    api = next((p for p in profiles.values() if not p.is_local), None)
    return [p for p in (local, api) if p is not None]


def _best(prompt: str, profile: ModelProfile, *, profile_aware: bool) -> tuple[str, float]:
    normalized = normalize(Prompt(text=prompt))
    scorer = IntegratedScorer(profile_aware=profile_aware)
    config = StrategyConfig()
    best_strategy = "none"
    best_score = 0.0
    for strategy in select(normalized, profile):
        candidate = strategy.apply(normalized, profile, config)
        report = validate(candidate, profile)
        if not report.ok:
            continue
        score = scorer.score(candidate, profile, report, task=normalized.detected_task)
        if score.integrated >= best_score:
            best_strategy, best_score = strategy.name.value, score.integrated
    return best_strategy, best_score


def main() -> None:
    profiles = load_profiles(_PROFILES_DIR)
    for profile in _pick_profiles(profiles):
        kind = "local" if profile.is_local else "api"
        print(f"\n== {profile.name} ({kind}) ==")
        print(f"{'task':<14} {'strategy':<20} {'base':>7} {'aware':>7} {'delta':>7}")
        for prompt in PROMPTS:
            task = normalize(Prompt(text=prompt)).detected_task
            base_strategy, base_score = _best(prompt, profile, profile_aware=False)
            aware_strategy, aware_score = _best(prompt, profile, profile_aware=True)
            flag = " *" if aware_strategy != base_strategy else ""
            print(
                f"{task:<14} {aware_strategy + flag:<20} "
                f"{base_score:>7.3f} {aware_score:>7.3f} {aware_score - base_score:>+7.3f}"
            )


if __name__ == "__main__":
    main()

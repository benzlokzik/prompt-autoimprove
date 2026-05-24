"""Run pai pipeline against a local Ollama model and capture metrics.

Usage: uv run python scripts/local_e2e.py <profile-name> <ollama-tag>
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

from prompt_autoimprove.adapters.base import GenerationRequest
from prompt_autoimprove.adapters.openai_compat import OpenAICompatAdapter
from prompt_autoimprove.config import ClassifierSettings
from prompt_autoimprove.core.complexity import HeuristicClassifier, build_classifier
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.core.strategies.llm_rewrite import LLMRewriter
from prompt_autoimprove.domain.prompt import Prompt
from prompt_autoimprove.registry.loader import load_profiles
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator

HARD_PROMPT = (
    "Refactor this 600-line billing reconciliation service to separate validation, "
    "persistence, and retry logic. Identify hot paths, propose data structures, "
    "and write unit tests step by step. Prove correctness against partial failures "
    "and produce a structured migration plan with rollback criteria."
)

_PROFILES_DIR = Path(__file__).resolve().parents[1] / "src/prompt_autoimprove/registry/profiles"


async def main(profile_name: str, ollama_tag: str) -> None:
    profiles = load_profiles(_PROFILES_DIR)
    if profile_name not in profiles:
        print(f"profile '{profile_name}' not in registry; create the YAML first")
        sys.exit(2)
    profile = profiles[profile_name]
    adapter = OpenAICompatAdapter(
        profile=profile,
        base_url="http://localhost:11434",
        model=ollama_tag,
    )

    rewriter = LLMRewriter(improver=adapter, max_output_tokens=512)
    classifier = build_classifier(
        ClassifierSettings(backend="composite"),
        improver=adapter,
    )
    orch = AutoImproveOrchestrator(
        profiles=profiles,
        adapters={profile.name: adapter},
        router=Router(policy=RoutingPolicy(), adapters={profile.name: adapter}),
        scorer=IntegratedScorer(),
        events=EventPublisher(),
        rewriter=rewriter,
        classifier=classifier,
    )

    # Pre-flight: a tiny generation to surface obvious errors.
    pre = await adapter.generate(GenerationRequest(prompt="hi", max_tokens=4))
    print(f"preflight: {pre.text[:40]!r}")

    t0 = time.perf_counter()
    result = await orch.run(Prompt(text=HARD_PROMPT), profile.name, probation=False)
    elapsed = time.perf_counter() - t0

    # Baseline: run heuristic-only score against the same prompt for delta.
    heuristic = HeuristicClassifier().classify(result.normalized)

    print(f"\n== {profile.name} / {ollama_tag} ==")
    print(f"elapsed_seconds: {elapsed:.2f}")
    print(f"complexity_label: {result.complexity.label if result.complexity else 'n/a'}")
    print(f"complexity_score: {result.complexity.score if result.complexity else 'n/a'}")
    print(f"heuristic_label: {heuristic.label}")
    print(f"heuristic_score: {heuristic.score}")
    print(f"chosen_strategy: {result.chosen.strategy.value}")
    print(f"integrated_score: {result.score.integrated:.3f}")
    print("candidates: " + ", ".join(c.strategy.value for c in result.candidates))
    llm_candidate = next((c for c in result.candidates if c.strategy.value == "llm_rewrite"), None)
    if llm_candidate is not None:
        print(f"\n--- llm_rewrite candidate ({len(llm_candidate.text)}c) ---")
        print(llm_candidate.text[:1200])
        print("--- end ---")
    print("\n--- chosen prompt ---")
    print(result.chosen.text[:600])
    print("--- end ---")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(64)
    asyncio.run(main(sys.argv[1], sys.argv[2]))

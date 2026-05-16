import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from prompt_autoimprove.adapters.circuit_breaker import CircuitBreakerAdapter
from prompt_autoimprove.adapters.factory import build_adapters_from_env
from prompt_autoimprove.config import get_settings
from prompt_autoimprove.core.complexity import build_classifier
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.core.strategies.llm_rewrite import LLMRewriter
from prompt_autoimprove.domain.prompt import Prompt
from prompt_autoimprove.registry.loader import load_profiles, resolve_profile
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator

app = typer.Typer(no_args_is_help=True, add_completion=False, name="pai")
console = Console()


def _build_orchestrator() -> AutoImproveOrchestrator:
    settings = get_settings()
    profiles = load_profiles(Path(settings.profiles_dir))
    publisher = EventPublisher()
    raw = build_adapters_from_env(profiles)
    adapters: dict = {name: CircuitBreakerAdapter(inner=ad) for name, ad in raw.items()}

    rewriter: LLMRewriter | None = None
    improver_adapter = None
    if settings.improver.profile is not None:
        improver_adapter = adapters.get(settings.improver.profile)
        if improver_adapter is None:
            try:
                improver_profile = resolve_profile(profiles, settings.improver.profile)
                improver_adapter = adapters.get(improver_profile.name)
            except KeyError:
                improver_adapter = None
        if improver_adapter is not None:
            rewriter = LLMRewriter(
                improver=improver_adapter,
                max_output_tokens=settings.improver.max_output_tokens,
            )

    classifier = build_classifier(settings.classifier, improver=improver_adapter)

    return AutoImproveOrchestrator(
        profiles=profiles,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=publisher,
        rewriter=rewriter,
        classifier=classifier,
    )


@app.command()
def improve(
    prompt: str = typer.Option(..., "--prompt", "-p", help="The prompt to improve"),
    profile: str = typer.Option(
        "qwen",
        "--profile",
        help="Target model family (e.g. claude, gpt, qwen, llama, gemma) or specific model name",
    ),
    locale: str | None = typer.Option(None, "--locale", help="Locale hint, e.g. en, ru"),
    sensitive: bool = typer.Option(False, "--sensitive", help="Force local-only routing"),
) -> None:
    orch = _build_orchestrator()

    async def _run() -> None:
        await orch.events.start()
        try:
            result = await orch.run(
                Prompt(text=prompt, locale_hint=locale), profile, sensitive=sensitive
            )
        finally:
            await orch.events.stop()

        console.rule(f"[bold green]Strategy: {result.chosen.strategy.value}")
        console.print(f"[bold]Rationale:[/] {result.chosen.rationale}")
        console.print(f"[bold]Score:[/] {result.score.integrated:.3f}")
        console.print()
        console.print("[bold]Candidate prompt:[/]")
        console.print(result.chosen.text)
        console.print()
        console.print("[bold]Explanation:[/]")
        console.print(result.run.explanation)
        if result.probation is not None:
            console.print()
            console.print("[bold]Probation output:[/]")
            console.print(result.probation.text)

    asyncio.run(_run())


@app.command()
def profiles() -> None:
    settings = get_settings()
    items = load_profiles(Path(settings.profiles_dir))
    table = Table(title="Model profiles")
    for col in ("name", "family", "format", "ctx", "vision", "reasoning"):
        table.add_column(col)
    for p in items.values():
        table.add_row(
            p.name,
            p.family.value,
            p.format.value,
            str(p.context_window),
            "yes" if p.supports_vision else "no",
            p.reasoning_mode.value,
        )
    console.print(table)


if __name__ == "__main__":
    app()

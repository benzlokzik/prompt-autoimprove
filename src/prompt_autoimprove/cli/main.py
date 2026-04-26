import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from prompt_autoimprove.config import get_settings
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.domain.prompt import Prompt
from prompt_autoimprove.registry.loader import load_profiles
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator

app = typer.Typer(no_args_is_help=True, add_completion=False, name="pai")
console = Console()


def _build_orchestrator() -> AutoImproveOrchestrator:
    settings = get_settings()
    profiles = load_profiles(Path(settings.profiles_dir))
    publisher = EventPublisher()
    adapters: dict = {}
    return AutoImproveOrchestrator(
        profiles=profiles,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(),
        events=publisher,
    )


@app.command()
def improve(
    prompt: str = typer.Option(..., "--prompt", "-p", help="The prompt to improve"),
    profile: str = typer.Option("qwen3-7b", "--profile", help="Target model profile"),
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

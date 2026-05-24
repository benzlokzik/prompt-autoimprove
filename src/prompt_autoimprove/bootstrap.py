from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from prompt_autoimprove.adapters.factory import build_adapters_from_env
from prompt_autoimprove.config import Settings
from prompt_autoimprove.core.complexity import build_classifier
from prompt_autoimprove.core.evaluator import IntegratedScorer
from prompt_autoimprove.core.semantic import EmbeddingSimilarity, SemanticSimilarity
from prompt_autoimprove.core.strategies.llm_rewrite import LLMRewriter
from prompt_autoimprove.logging import get_logger
from prompt_autoimprove.persistence.models import Base
from prompt_autoimprove.registry.loader import load_profiles, resolve_profile
from prompt_autoimprove.routing.router import Router, RoutingPolicy
from prompt_autoimprove.services.kafka_producer import EventPublisher
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator

logger = get_logger(__name__)


@dataclass(slots=True)
class RuntimeContext:
    orchestrator: AutoImproveOrchestrator
    profiles: dict
    publisher: EventPublisher
    session_factory: async_sessionmaker | None


async def _make_session_factory(settings: Settings) -> async_sessionmaker | None:
    try:
        engine = create_async_engine(settings.db.dsn, echo=settings.db.echo, future=True)
        if settings.db.auto_create:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        else:
            async with engine.connect():
                pass
        return async_sessionmaker(engine, expire_on_commit=False)
    except Exception as exc:
        logger.warning("persistence.unavailable", error=str(exc))
        return None


async def build_runtime(settings: Settings) -> RuntimeContext:
    """Build the shared pipeline runtime used by both the HTTP and gRPC servers."""
    profiles = load_profiles(Path(settings.profiles_dir))
    adapters = build_adapters_from_env(profiles)
    publisher = EventPublisher()
    await publisher.start()
    session_factory = await _make_session_factory(settings)

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

    semantic: SemanticSimilarity | None = None
    if settings.scorer.semantic:
        semantic = EmbeddingSimilarity(
            model_name=settings.scorer.embedding_model,
            device=settings.scorer.device,
        )

    orchestrator = AutoImproveOrchestrator(
        profiles=profiles,
        adapters=adapters,
        router=Router(policy=RoutingPolicy(), adapters=adapters),
        scorer=IntegratedScorer(semantic=semantic, semantic_blend=settings.scorer.semantic_blend),
        events=publisher,
        session_factory=session_factory,
        rewriter=rewriter,
        classifier=classifier,
    )
    return RuntimeContext(
        orchestrator=orchestrator,
        profiles=profiles,
        publisher=publisher,
        session_factory=session_factory,
    )


async def shutdown_runtime(ctx: RuntimeContext) -> None:
    try:
        await ctx.publisher.stop()
    except Exception as exc:
        logger.warning("publisher.stop_failed", error=str(exc))

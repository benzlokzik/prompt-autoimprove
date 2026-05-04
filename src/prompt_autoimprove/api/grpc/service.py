from collections.abc import AsyncIterator
from typing import Any

import prompt_autoimprove.api.grpc.generated  # noqa: F401

from autoimprove.v1 import autoimprove_pb2 as pb  # isort: skip
from autoimprove.v1 import autoimprove_pb2_grpc as pb_grpc  # isort: skip

from prompt_autoimprove.domain.prompt import Modality, Prompt, PromptAttachment
from prompt_autoimprove.services.orchestrator import AutoImproveOrchestrator


class AutoImproveService(pb_grpc.AutoImproveServicer):
    def __init__(self, orchestrator: AutoImproveOrchestrator) -> None:
        self.orchestrator = orchestrator

    async def Improve(self, request: Any, context: Any) -> AsyncIterator[Any]:  # noqa: ARG002
        prompt = Prompt(
            text=request.prompt,
            locale_hint=request.locale_hint or None,
            modality=Modality.TEXT,
            attachments=[
                PromptAttachment(
                    modality=Modality(att.modality),
                    uri=att.uri,
                    mime_type=att.mime_type,
                    bytes_size=att.bytes_size,
                )
                for att in request.attachments
            ],
        )
        result = await self.orchestrator.run(prompt, request.profile, sensitive=request.sensitive)

        yield pb.ImproveEvent(
            stage="normalized",
            normalization=pb.Normalization(
                language=result.normalized.detected_language,
                task=result.normalized.detected_task,
                missing_parameters=list(result.normalized.missing_parameters),
                safety_flags=list(result.normalized.safety_flags),
            ),
        )
        yield pb.ImproveEvent(
            stage="strategy_selected",
            strategy_selected=pb.StrategySelected(
                strategy=result.chosen.strategy.value,
                reason=result.chosen.rationale,
            ),
        )
        yield pb.ImproveEvent(
            stage="candidate",
            candidate=pb.Candidate(
                text=result.chosen.text,
                rationale=result.chosen.rationale,
                estimated_tokens=result.chosen.estimated_tokens,
            ),
        )
        for metric in result.score.metrics:
            yield pb.ImproveEvent(
                stage="partial_eval",
                partial_eval=pb.PartialEval(
                    metric=metric.name.value,
                    value=metric.value,
                    weight=metric.weight,
                ),
            )
        yield pb.ImproveEvent(
            stage="final_decision",
            final_decision=pb.FinalDecision(
                integrated_score=result.score.integrated,
                explanation=result.run.explanation,
                adapter=result.routing.adapter_name,
                profile=result.routing.profile.name,
            ),
        )

from fastapi import APIRouter, Depends, HTTPException, Request, status

from prompt_autoimprove.api.http.auth import require_api_key
from prompt_autoimprove.api.http.schemas import ImproveRequest, ImproveResponse, MetricOut
from prompt_autoimprove.domain.prompt import Prompt

router = APIRouter(prefix="/v1", tags=["improve"])


@router.post("/improve", response_model=ImproveResponse)
async def improve(
    body: ImproveRequest,
    request: Request,
    _: str = Depends(require_api_key),
) -> ImproveResponse:
    orchestrator = request.app.state.orchestrator
    profiles = request.app.state.profiles
    if body.profile not in profiles:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"unknown profile {body.profile!r}")
    prompt = Prompt(text=body.prompt, locale_hint=body.locale_hint)
    result = await orchestrator.run(prompt, body.profile, sensitive=body.sensitive)
    return ImproveResponse(
        strategy=result.chosen.strategy.value,
        candidate=result.chosen.text,
        rationale=result.chosen.rationale,
        score=result.score.integrated,
        metrics=[
            MetricOut(name=m.name.value, value=m.value, weight=m.weight)
            for m in result.score.metrics
        ],
        explanation=result.run.explanation,
    )

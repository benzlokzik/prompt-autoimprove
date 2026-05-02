from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi.util import get_remote_address

from prompt_autoimprove.api.http.auth import require_api_key
from prompt_autoimprove.api.http.rate_limit import limiter
from prompt_autoimprove.api.http.schemas import ImproveRequest, ImproveResponse, MetricOut
from prompt_autoimprove.config import get_settings
from prompt_autoimprove.domain.prompt import Prompt

router = APIRouter(prefix="/v1", tags=["improve"])


def _rate_key(request: Request) -> str:
    return request.headers.get("x-api-key") or get_remote_address(request)


@router.post("/improve", response_model=ImproveResponse)
@limiter.limit(
    lambda: f"{get_settings().api.rate_limit_per_minute}/minute", key_func=_rate_key
)
async def improve(
    request: Request,
    body: ImproveRequest,
    _: str = Depends(require_api_key),
) -> ImproveResponse:
    orchestrator = request.app.state.orchestrator
    profiles = request.app.state.profiles
    if body.profile not in profiles:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"unknown profile {body.profile!r}")
    prompt = Prompt(text=body.prompt, locale_hint=body.locale_hint)
    result = await orchestrator.run(
        prompt, body.profile, sensitive=body.sensitive, session_id=body.session_ref
    )
    return ImproveResponse(
        session_id=str(result.session_id),
        strategy=result.chosen.strategy.value,
        candidate=result.chosen.text,
        rationale=result.chosen.rationale,
        score=result.score.integrated,
        metrics=[
            MetricOut(name=m.name.value, value=m.value, weight=m.weight)
            for m in result.score.metrics
        ],
        explanation=result.run.explanation,
        probation=result.probation.text if result.probation else None,
    )

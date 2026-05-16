from fastapi import APIRouter, Depends, Request

from prompt_autoimprove.api.http.auth import require_api_key
from prompt_autoimprove.api.http.schemas import ProfileOut

router = APIRouter(prefix="/v1", tags=["profiles"])


@router.get("/profiles", response_model=list[ProfileOut])
async def list_profiles(request: Request, _: str = Depends(require_api_key)) -> list[ProfileOut]:
    return [
        ProfileOut(
            name=p.name,
            family=p.family.value,
            format=p.format.value,
            context_window=p.context_window,
            max_output_tokens=p.max_output_tokens,
            supports_vision=p.supports_vision,
            reasoning_mode=p.reasoning_mode.value,
            cost_per_1k_input=p.cost_per_1k_input,
            cost_per_1k_output=p.cost_per_1k_output,
            p50_latency_ms=p.p50_latency_ms,
            supports_tools=p.supports_tools,
            family_default=p.family_default,
        )
        for p in request.app.state.profiles.values()
    ]

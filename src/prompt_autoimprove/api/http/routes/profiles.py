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
            supports_vision=p.supports_vision,
        )
        for p in request.app.state.profiles.values()
    ]

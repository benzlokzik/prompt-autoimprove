from fastapi import APIRouter, Depends, HTTPException, status

from prompt_autoimprove.api.http.auth import require_api_key
from prompt_autoimprove.api.http.schemas import HistoryItem

router = APIRouter(prefix="/v1", tags=["history"])


@router.get("/history/{session_id}", response_model=list[HistoryItem])
async def session_history(
    session_id: str,
    _: str = Depends(require_api_key),
) -> list[HistoryItem]:
    if not session_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="session_id required")
    return []

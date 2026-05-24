from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz(request: Request) -> dict[str, object]:
    state = request.app.state
    return {
        "status": "ok",
        "orchestrator": getattr(state, "orchestrator", None) is not None,
        "persistence": getattr(state, "session_factory", None) is not None,
    }

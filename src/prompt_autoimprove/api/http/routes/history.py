from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from prompt_autoimprove.api.http.auth import require_api_key
from prompt_autoimprove.api.http.schemas import HistoryItem, HistoryRevision
from prompt_autoimprove.persistence.models import PromptRow, SessionRow

router = APIRouter(prefix="/v1", tags=["history"])


@router.get("/history/{session_ref}", response_model=list[HistoryItem])
async def session_history(
    session_ref: str,
    request: Request,
    _: str = Depends(require_api_key),
) -> list[HistoryItem]:
    factory = getattr(request.app.state, "session_factory", None)
    if factory is None:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="persistence is not configured"
        )

    # A non-UUID ref is treated as a user_ref, not an error — both are valid lookups.
    try:
        sid: UUID | None = UUID(session_ref)
    except ValueError:
        sid = None

    try:
        async with factory() as db:
            if sid is None:
                session_row = (
                    await db.execute(select(SessionRow).where(SessionRow.user_ref == session_ref))
                ).scalar_one_or_none()
                if session_row is None:
                    return []
                sid = session_row.id

            rows = (
                (
                    await db.execute(
                        select(PromptRow)
                        .where(PromptRow.session_id == sid)
                        .order_by(PromptRow.created_at.desc())
                        .options(selectinload(PromptRow.revisions))
                    )
                )
                .scalars()
                .all()
            )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="history lookup failed"
        ) from exc

    return [
        HistoryItem(
            prompt_id=str(p.id),
            text=p.text,
            modality=p.modality,
            created_at=p.created_at.isoformat(),
            revisions=[
                HistoryRevision(
                    revision_id=str(r.id),
                    text=r.text,
                    strategy=r.strategy,
                    rationale=r.rationale,
                    created_at=r.created_at.isoformat(),
                )
                for r in p.revisions
            ],
        )
        for p in rows
    ]

from pydantic import BaseModel, Field


class ImproveRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=20000)
    profile: str
    locale_hint: str | None = None
    sensitive: bool = False
    session_ref: str | None = None


class MetricOut(BaseModel):
    name: str
    value: float
    weight: float


class ImproveResponse(BaseModel):
    session_id: str
    strategy: str
    candidate: str
    rationale: str
    score: float
    metrics: list[MetricOut]
    explanation: str
    probation: str | None = None


class ProfileOut(BaseModel):
    name: str
    family: str
    format: str
    context_window: int
    supports_vision: bool


class HistoryRevision(BaseModel):
    revision_id: str
    text: str
    strategy: str
    rationale: str
    created_at: str


class HistoryItem(BaseModel):
    prompt_id: str
    text: str
    modality: str
    created_at: str
    revisions: list[HistoryRevision]

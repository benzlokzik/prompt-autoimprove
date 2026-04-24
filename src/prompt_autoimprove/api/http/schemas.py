from pydantic import BaseModel, Field


class ImproveRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=20000)
    profile: str
    locale_hint: str | None = None
    sensitive: bool = False


class MetricOut(BaseModel):
    name: str
    value: float
    weight: float


class ImproveResponse(BaseModel):
    strategy: str
    candidate: str
    rationale: str
    score: float
    metrics: list[MetricOut]
    explanation: str


class ProfileOut(BaseModel):
    name: str
    family: str
    format: str
    context_window: int
    supports_vision: bool


class HistoryItem(BaseModel):
    prompt_id: str
    text: str
    created_at: str

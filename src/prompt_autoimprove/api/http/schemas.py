from typing import Literal

from pydantic import BaseModel, Field


class AttachmentIn(BaseModel):
    modality: Literal["text", "image", "audio", "mixed"] = "image"
    uri: str = Field(..., max_length=15_000_000)
    mime_type: str = "application/octet-stream"
    bytes_size: int = 0


class ImproveRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=20000)
    profile: str
    locale_hint: str | None = None
    sensitive: bool = False
    session_ref: str | None = None
    attachments: list[AttachmentIn] = Field(default_factory=list, max_length=8)


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
    max_output_tokens: int = 0
    supports_vision: bool
    reasoning_mode: str = "none"
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    p50_latency_ms: int = 0
    supports_tools: bool = False
    family_default: bool = False


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

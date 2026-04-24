from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class Modality(StrEnum):
    """Supported input modalities for a prompt."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MIXED = "mixed"


@dataclass(slots=True, frozen=True)
class PromptAttachment:
    """A binary or referenced attachment carried with a prompt."""

    modality: Modality
    uri: str
    mime_type: str
    bytes_size: int = 0


@dataclass(slots=True)
class Prompt:
    """A user-supplied prompt as received by the system."""

    text: str
    modality: Modality = Modality.TEXT
    attachments: list[PromptAttachment] = field(default_factory=list)
    locale_hint: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class PromptRevision:
    """A derived version of a prompt produced by a strategy."""

    prompt_id: UUID
    text: str
    strategy: str
    rationale: str
    parent_revision_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True, frozen=True)
class NormalizedPrompt:
    """Result of the normalization stage."""

    source: Prompt
    cleaned_text: str
    detected_language: str
    detected_task: str
    missing_parameters: tuple[str, ...]
    safety_flags: tuple[str, ...]

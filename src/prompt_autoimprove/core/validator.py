from __future__ import annotations

from dataclasses import dataclass

from prompt_autoimprove.core.strategies.base import CandidatePrompt
from prompt_autoimprove.domain.model_profile import ModelProfile

_FORBIDDEN_FRAGMENTS = (
    "ignore previous instructions",
    "<|im_start|>system",
    "забудь все инструкции",
)


@dataclass(slots=True, frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"


@dataclass(slots=True, frozen=True)
class ValidationReport:
    candidate_id: str
    issues: tuple[ValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return all(issue.severity != "error" for issue in self.issues)


def validate(candidate: CandidatePrompt, profile: ModelProfile) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if candidate.estimated_tokens > profile.context_window:
        issues.append(
            ValidationIssue(
                "too_long",
                f"{candidate.estimated_tokens} tokens exceeds context {profile.context_window}",
            )
        )

    if not candidate.text.strip():
        issues.append(ValidationIssue("empty", "Candidate is empty after normalization"))

    lowered = candidate.text.lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        if fragment in lowered:
            issues.append(ValidationIssue("unsafe", f"Contains forbidden fragment: {fragment!r}"))

    if "respond with a single json object" in lowered and "no prose" not in lowered:
        issues.append(
            ValidationIssue("format_drift", "JSON contract weakened", severity="warning")
        )

    return ValidationReport(candidate_id=str(candidate.id), issues=tuple(issues))

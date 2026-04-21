"""Task type taxonomy used by the normalizer and strategy selector."""

from __future__ import annotations

from enum import StrEnum


class TaskType(StrEnum):
    """High-level task category inferred from the user prompt."""

    QA = "qa"
    SUMMARIZE = "summarize"
    EXTRACT = "extract"
    CODE_GENERATE = "code_generate"
    CODE_EXPLAIN = "code_explain"
    REWRITE = "rewrite"
    TRANSLATE = "translate"
    CLASSIFY = "classify"
    REASONING = "reasoning"
    VISION = "vision"
    OTHER = "other"


REASONING_HEAVY: frozenset[TaskType] = frozenset(
    {TaskType.REASONING, TaskType.CODE_GENERATE, TaskType.EXTRACT}
)
"""Tasks that benefit from chain-decomposition and self-verification."""

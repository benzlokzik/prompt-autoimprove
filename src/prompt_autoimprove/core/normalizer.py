import re
import unicodedata
from collections.abc import Iterable

from prompt_autoimprove.domain.prompt import NormalizedPrompt, Prompt
from prompt_autoimprove.domain.task_type import TaskType

_TASK_KEYWORDS: dict[TaskType, tuple[str, ...]] = {
    TaskType.SUMMARIZE: ("summarize", "tl;dr", "сократи", "резюме"),
    TaskType.EXTRACT: ("extract", "list all", "найди", "извлеки"),
    TaskType.CODE_GENERATE: ("write code", "implement", "напиши код", "функцию"),
    TaskType.CODE_EXPLAIN: ("explain this code", "what does this code", "объясни код"),
    TaskType.REWRITE: ("rewrite", "rephrase", "переформулируй"),
    TaskType.TRANSLATE: ("translate", "переведи"),
    TaskType.CLASSIFY: ("classify", "categorize", "классифицируй"),
    TaskType.REASONING: ("prove", "step by step", "почему", "докажи"),
    TaskType.QA: ("?", "how", "what", "why", "когда", "что"),
}

_RU_RE = re.compile(r"[Ѐ-ӿ]")
_FORBIDDEN = (
    "ignore previous instructions",
    "system prompt:",
    "<|im_start|>system",
    "забудь все инструкции",
)
_PARAM_PATTERNS = (
    re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"),
    re.compile(r"<<([A-Z_]+)>>"),
)

_PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"(?:\+?\d[\d\s\-().]{8,}\d)"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}


def detect_language(text: str) -> str:
    """Coarse language detection: ru vs en, fallback to en."""
    if _RU_RE.search(text):
        return "ru"
    return "en"


def detect_task(text: str) -> TaskType:
    """Heuristic task classifier based on keyword presence."""
    lowered = text.lower()
    for task, keywords in _TASK_KEYWORDS.items():
        if any(k in lowered for k in keywords):
            return task
    return TaskType.OTHER


def find_missing_parameters(text: str) -> tuple[str, ...]:
    """Return any unfilled `{name}` or `<<NAME>>` placeholders."""
    found: list[str] = []
    for pattern in _PARAM_PATTERNS:
        found.extend(pattern.findall(text))
    seen: dict[str, None] = {}
    for name in found:
        seen.setdefault(name, None)
    return tuple(seen)


def detect_safety_flags(text: str) -> tuple[str, ...]:
    """Return safety flags raised by simple substring matching."""
    lowered = text.lower()
    return tuple(flag for flag in _FORBIDDEN if flag in lowered)


def detect_pii(text: str) -> tuple[str, ...]:
    """Return PII categories observed in the text."""
    return tuple(name for name, pattern in _PII_PATTERNS.items() if pattern.search(text))


def redact_pii(text: str) -> str:
    """Replace observed PII with category placeholders."""
    redacted = text
    for name, pattern in _PII_PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED:{name}]", redacted)
    return redacted


def _strip_control(text: str) -> str:
    return "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in "\n\t")


def normalize(
    prompt: Prompt,
    *,
    extra_safety: Iterable[str] = (),
    redact: bool = True,
) -> NormalizedPrompt:
    """Run the full normalization pipeline on a prompt."""
    cleaned = _strip_control(prompt.text).strip()
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    pii_categories = detect_pii(cleaned)
    if redact and pii_categories:
        cleaned = redact_pii(cleaned)

    language = prompt.locale_hint or detect_language(cleaned)
    task = detect_task(cleaned)
    missing = find_missing_parameters(cleaned)
    safety = detect_safety_flags(cleaned)
    if pii_categories:
        safety = (*safety, *(f"pii:{c}" for c in pii_categories))
    if extra_safety:
        safety = (*safety, *(s for s in extra_safety if s in cleaned.lower()))

    return NormalizedPrompt(
        source=prompt,
        cleaned_text=cleaned,
        detected_language=language,
        detected_task=task.value,
        missing_parameters=missing,
        safety_flags=safety,
    )

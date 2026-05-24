from __future__ import annotations

import functools
from typing import Any


def _heuristic(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


@functools.lru_cache(maxsize=1)
def _encoder() -> Any:
    """Return a cached tiktoken encoder, or None when tiktoken is unavailable."""
    try:
        import tiktoken

        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def count_tokens(text: str) -> int:
    """Count tokens with a real BPE tokenizer when present, else a ~4-chars heuristic."""
    encoder = _encoder()
    if encoder is None:
        return _heuristic(text)
    try:
        return max(1, len(encoder.encode(text)))
    except Exception:
        return _heuristic(text)

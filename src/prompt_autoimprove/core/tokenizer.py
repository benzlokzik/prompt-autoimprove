from __future__ import annotations

import functools
from typing import Any

_DEFAULT_ENCODING = "cl100k_base"


def _heuristic(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


@functools.lru_cache(maxsize=16)
def _encoder(model: str | None) -> Any:
    """Return a cached tiktoken encoder for ``model``, or None when unavailable.

    Known OpenAI models get their exact encoding (e.g. gpt-4o -> o200k_base);
    everything else (claude, qwen, gemma, ...) falls back to cl100k_base.
    """
    try:
        import tiktoken

        if model:
            try:
                return tiktoken.encoding_for_model(model)
            except KeyError:
                pass
        return tiktoken.get_encoding(_DEFAULT_ENCODING)
    except Exception:
        return None


def count_tokens(text: str, model: str | None = None) -> int:
    """Count tokens with the model's BPE tokenizer when present, else a heuristic."""
    encoder = _encoder(model)
    if encoder is None:
        return _heuristic(text)
    try:
        return max(1, len(encoder.encode(text)))
    except Exception:
        return _heuristic(text)

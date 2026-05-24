from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


class SpamUnavailable(Exception):
    pass


@runtime_checkable
class SpamSignal(Protocol):
    def score(self, text: str) -> float: ...


@dataclass(slots=True)
class BertSpamSignal:
    """P(spam) for Russian text from a fine-tuned BERT classifier (moderation group)."""

    pretrained: str = "cointegrated/rubert-tiny2"
    _model: Any = field(init=False, default=None, repr=False)

    def _ensure_ready(self) -> None:
        if self._model is not None:
            return
        try:
            from spam_detector.core.base_model import ModelConfig
            from spam_detector.transformers.bert_model import BertSpamModel, BertTrainingConfig
        except ImportError as exc:
            raise SpamUnavailable("install: uv sync --group moderation") from exc
        model = BertSpamModel(ModelConfig(), BertTrainingConfig(pretrained=self.pretrained))
        model.load()
        self._model = model

    def score(self, text: str) -> float:
        self._ensure_ready()
        return max(0.0, min(1.0, float(self._model.predict_proba(text))))

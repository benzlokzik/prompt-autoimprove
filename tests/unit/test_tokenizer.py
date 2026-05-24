import prompt_autoimprove.core.tokenizer as tok
from prompt_autoimprove.core.strategies.base import estimate_tokens


def test_heuristic_when_encoder_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(tok, "_encoder", lambda: None)
    assert tok.count_tokens("abcd") == 1
    assert tok.count_tokens("a" * 40) == 10
    assert tok.count_tokens("") == 1


def test_uses_encoder_when_available(monkeypatch) -> None:
    class FakeEncoder:
        def encode(self, text: str) -> list[str]:
            return text.split()

    monkeypatch.setattr(tok, "_encoder", FakeEncoder)
    assert tok.count_tokens("a b c") == 3
    assert tok.count_tokens("") == 1


def test_falls_back_when_encoder_raises(monkeypatch) -> None:
    class BadEncoder:
        def encode(self, text: str) -> list[str]:
            raise RuntimeError("boom")

    monkeypatch.setattr(tok, "_encoder", BadEncoder)
    assert tok.count_tokens("a" * 40) == 10


def test_estimate_tokens_delegates_to_count_tokens() -> None:
    assert estimate_tokens("hello world") >= 1

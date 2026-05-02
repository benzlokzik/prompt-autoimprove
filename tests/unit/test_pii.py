from prompt_autoimprove.core.normalizer import detect_pii, normalize, redact_pii
from prompt_autoimprove.domain.prompt import Prompt


def test_detect_email_and_phone() -> None:
    text = "Contact alice@example.com or call +1 555 123 4567"
    assert "email" in detect_pii(text)
    assert "phone" in detect_pii(text)


def test_redact_replaces_pii_inline() -> None:
    text = "Email me at bob@example.org"
    redacted = redact_pii(text)
    assert "bob@example.org" not in redacted
    assert "[REDACTED:email]" in redacted


def test_normalize_redacts_and_flags_pii() -> None:
    prompt = Prompt(text="Send report to carol@example.com please")
    out = normalize(prompt)
    assert "carol@example.com" not in out.cleaned_text
    assert "pii:email" in out.safety_flags


def test_normalize_can_skip_redaction() -> None:
    prompt = Prompt(text="Send to dave@example.com")
    out = normalize(prompt, redact=False)
    assert "dave@example.com" in out.cleaned_text
    assert "pii:email" in out.safety_flags

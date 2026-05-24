import pytest

from prompt_autoimprove.config import Settings


def test_dev_environment_defaults_to_dev_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PAI_API__API_KEY", raising=False)
    monkeypatch.setenv("PAI_ENVIRONMENT", "dev")
    settings = Settings()
    assert settings.api.api_key == "dev-key"


def test_production_without_key_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PAI_API__API_KEY", raising=False)
    monkeypatch.setenv("PAI_ENVIRONMENT", "production")
    with pytest.raises(ValueError, match="API key is required"):
        Settings()


def test_production_with_explicit_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAI_ENVIRONMENT", "production")
    monkeypatch.setenv("PAI_API__API_KEY", "real-secret")
    settings = Settings()
    assert settings.api.api_key == "real-secret"


def test_allow_dev_key_escape_hatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PAI_API__API_KEY", raising=False)
    monkeypatch.setenv("PAI_ENVIRONMENT", "production")
    monkeypatch.setenv("PAI_API__ALLOW_DEV_KEY", "1")
    settings = Settings()
    assert settings.api.api_key == "dev-key"

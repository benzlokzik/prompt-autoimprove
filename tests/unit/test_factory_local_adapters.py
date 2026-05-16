from pathlib import Path

import pytest

from prompt_autoimprove.adapters.factory import build_adapters_from_env
from prompt_autoimprove.adapters.gguf_local import GGUFAdapter
from prompt_autoimprove.adapters.openai_compat import OpenAICompatAdapter
from prompt_autoimprove.adapters.safetensors_hf import SafetensorsHFAdapter
from prompt_autoimprove.registry.loader import load_profiles

_REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILES = load_profiles(_REPO_ROOT / "src/prompt_autoimprove/registry/profiles")


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    for key in (
        "ANTHROPIC_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_API_KEY",
        "OPENAI_MODEL_NAME",
        "OPENAI_TARGET_PROFILE",
        "PAI_GGUF_MODEL_PATH",
        "PAI_GGUF_TARGET_PROFILE",
        "PAI_HF_MODEL_ID",
        "PAI_HF_TARGET_PROFILE",
    ):
        monkeypatch.delenv(key, raising=False)


def test_no_env_yields_empty(monkeypatch):
    assert build_adapters_from_env(PROFILES) == {}


def test_openai_compat_wires_when_target_is_api(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OPENAI_MODEL_NAME", "qwen2.5:1.5b-instruct")
    monkeypatch.setenv("OPENAI_TARGET_PROFILE", "ollama-qwen-1_5b")
    adapters = build_adapters_from_env(PROFILES)
    assert "ollama-qwen-1_5b" in adapters
    assert isinstance(adapters["ollama-qwen-1_5b"], OpenAICompatAdapter)


def test_gguf_wires_with_env(monkeypatch, tmp_path):
    fake = tmp_path / "model.gguf"
    fake.write_bytes(b"")
    monkeypatch.setenv("PAI_GGUF_MODEL_PATH", str(fake))
    monkeypatch.setenv("PAI_GGUF_TARGET_PROFILE", "qwen3-7b")
    adapters = build_adapters_from_env(PROFILES)
    assert "qwen3-7b" in adapters
    assert isinstance(adapters["qwen3-7b"], GGUFAdapter)


def test_hf_wires_with_env(monkeypatch):
    monkeypatch.setenv("PAI_HF_MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")
    monkeypatch.setenv("PAI_HF_TARGET_PROFILE", "qwen3-7b")
    adapters = build_adapters_from_env(PROFILES)
    assert "qwen3-7b" in adapters
    assert isinstance(adapters["qwen3-7b"], SafetensorsHFAdapter)


def test_unknown_target_silently_dropped(monkeypatch, tmp_path):
    fake = tmp_path / "x.gguf"
    fake.write_bytes(b"")
    monkeypatch.setenv("PAI_GGUF_MODEL_PATH", str(fake))
    monkeypatch.setenv("PAI_GGUF_TARGET_PROFILE", "nope")
    assert build_adapters_from_env(PROFILES) == {}

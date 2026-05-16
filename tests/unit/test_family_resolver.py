from pathlib import Path

import pytest

from prompt_autoimprove.domain.model_profile import ModelFamily, ModelFormat, ModelProfile
from prompt_autoimprove.registry.loader import (
    ProfileNotFoundError,
    list_families,
    load_profiles,
    resolve_profile,
)

PROFILES = Path(__file__).resolve().parents[2] / "src/prompt_autoimprove/registry/profiles"


def _profile(
    name: str,
    family: ModelFamily,
    *,
    family_default: bool = False,
    fmt: ModelFormat = ModelFormat.GGUF,
) -> ModelProfile:
    return ModelProfile(
        name=name,
        family=family,
        format=fmt,
        context_window=8192,
        max_output_tokens=1024,
        family_default=family_default,
    )


def test_resolve_by_specific_name() -> None:
    profiles = {p.name: p for p in [_profile("qwen3-7b", ModelFamily.QWEN, family_default=True)]}
    assert resolve_profile(profiles, "qwen3-7b").name == "qwen3-7b"


def test_resolve_family_picks_marked_default() -> None:
    profiles = {
        p.name: p
        for p in [
            _profile("claude-opus-4-7", ModelFamily.CLAUDE, fmt=ModelFormat.API),
            _profile(
                "claude-sonnet-4-6",
                ModelFamily.CLAUDE,
                family_default=True,
                fmt=ModelFormat.API,
            ),
        ]
    }
    assert resolve_profile(profiles, "claude").name == "claude-sonnet-4-6"


def test_resolve_family_falls_back_to_first_when_no_default() -> None:
    profiles = {p.name: p for p in [_profile("llama3-8b", ModelFamily.LLAMA)]}
    assert resolve_profile(profiles, "llama").name == "llama3-8b"


def test_resolve_unknown_raises() -> None:
    with pytest.raises(ProfileNotFoundError):
        resolve_profile({}, "nonsense")


def test_list_families_groups_loaded_profiles() -> None:
    profiles = load_profiles(PROFILES)
    grouped = list_families(profiles)
    assert ModelFamily.CLAUDE in grouped
    assert ModelFamily.GPT in grouped
    assert ModelFamily.GPT_OSS in grouped
    assert any(p.family_default for p in grouped[ModelFamily.CLAUDE])


def test_loaded_claude_profiles_use_claude_family() -> None:
    profiles = load_profiles(PROFILES)
    sonnet = profiles["claude-sonnet-4-6"]
    assert sonnet.family is ModelFamily.CLAUDE
    assert sonnet.family_default is True
    assert profiles["claude-opus-4-7"].family is ModelFamily.CLAUDE

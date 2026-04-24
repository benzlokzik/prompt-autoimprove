from pathlib import Path

import yaml

from prompt_autoimprove.domain.model_profile import (
    ModelFamily,
    ModelFormat,
    ModelProfile,
    ReasoningMode,
)


class ProfileNotFoundError(KeyError):
    pass


def _coerce(raw: dict[str, object]) -> ModelProfile:
    return ModelProfile(
        name=str(raw["name"]),
        family=ModelFamily(str(raw["family"])),
        format=ModelFormat(str(raw["format"])),
        context_window=int(raw["context_window"]),  # type: ignore[arg-type]
        max_output_tokens=int(raw["max_output_tokens"]),  # type: ignore[arg-type]
        supports_vision=bool(raw.get("supports_vision", False)),
        supports_tools=bool(raw.get("supports_tools", False)),
        reasoning_mode=ReasoningMode(str(raw.get("reasoning_mode", "none"))),
        cost_per_1k_input=float(raw.get("cost_per_1k_input", 0.0)),  # type: ignore[arg-type]
        cost_per_1k_output=float(raw.get("cost_per_1k_output", 0.0)),  # type: ignore[arg-type]
        p50_latency_ms=int(raw.get("p50_latency_ms", 0)),  # type: ignore[arg-type]
        tags=tuple(raw.get("tags", []) or ()),  # type: ignore[arg-type]
    )


def load_profiles(directory: Path) -> dict[str, ModelProfile]:
    profiles: dict[str, ModelProfile] = {}
    for path in sorted(directory.glob("*.yaml")):
        with path.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        profile = _coerce(raw)
        profiles[profile.name] = profile
    return profiles


def get_profile(profiles: dict[str, ModelProfile], name: str) -> ModelProfile:
    if name not in profiles:
        raise ProfileNotFoundError(name)
    return profiles[name]

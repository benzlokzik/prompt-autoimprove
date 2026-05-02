import os

from prompt_autoimprove.adapters.anthropic_api import AnthropicAdapter
from prompt_autoimprove.adapters.base import ModelAdapter
from prompt_autoimprove.adapters.openai_compat import OpenAICompatAdapter
from prompt_autoimprove.domain.model_profile import ModelFormat, ModelProfile

_CLAUDE_MODEL_BY_PROFILE = {
    "claude-opus-4-7": "claude-opus-4-7",
    "claude-sonnet-4-6": "claude-sonnet-4-6",
}


def build_adapters_from_env(profiles: dict[str, ModelProfile]) -> dict[str, ModelAdapter]:
    out: dict[str, ModelAdapter] = {}

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        for name, model in _CLAUDE_MODEL_BY_PROFILE.items():
            profile = profiles.get(name)
            if profile is None:
                continue
            out[name] = AnthropicAdapter(profile=profile, model=model, api_key=anthropic_key)

    openai_base = os.environ.get("OPENAI_BASE_URL")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    openai_model = os.environ.get("OPENAI_MODEL_NAME")
    openai_target = os.environ.get("OPENAI_TARGET_PROFILE")
    if openai_base and openai_target and openai_model:
        profile = profiles.get(openai_target)
        if profile is not None and profile.format is ModelFormat.API:
            out[openai_target] = OpenAICompatAdapter(
                profile=profile, base_url=openai_base, model=openai_model, api_key=openai_key
            )

    return out

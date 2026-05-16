from prompt_autoimprove.adapters.anthropic_api import AnthropicAdapter
from prompt_autoimprove.adapters.base import GenerationRequest
from prompt_autoimprove.adapters.openai_compat import OpenAICompatAdapter
from prompt_autoimprove.domain.model_profile import (
    ModelFamily,
    ModelFormat,
    ModelProfile,
)
from prompt_autoimprove.domain.prompt import Modality, PromptAttachment


def _profile(*, vision: bool) -> ModelProfile:
    return ModelProfile(
        name="m",
        family=ModelFamily.CLAUDE,
        format=ModelFormat.API,
        context_window=200_000,
        max_output_tokens=1024,
        supports_vision=vision,
    )


_REQ_WITH_IMAGE = GenerationRequest(
    prompt="Describe this image.",
    attachments=(
        PromptAttachment(
            modality=Modality.IMAGE, uri="https://example.com/x.png", mime_type="image/png"
        ),
    ),
)


def test_anthropic_payload_includes_image_block_when_vision_supported() -> None:
    adapter = AnthropicAdapter(profile=_profile(vision=True), model="claude-x", api_key="k")
    payload = adapter._payload(_REQ_WITH_IMAGE, stream=False)
    content = payload["messages"][0]["content"]
    assert isinstance(content, list)
    assert content[0]["type"] == "image"
    assert content[1]["type"] == "text"
    assert content[1]["text"] == "Describe this image."


def test_anthropic_payload_strips_images_when_vision_unsupported() -> None:
    adapter = AnthropicAdapter(profile=_profile(vision=False), model="claude-x", api_key="k")
    payload = adapter._payload(_REQ_WITH_IMAGE, stream=False)
    assert payload["messages"][0]["content"] == "Describe this image."


def test_openai_payload_includes_image_block_when_vision_supported() -> None:
    profile = ModelProfile(
        name="m",
        family=ModelFamily.GPT,
        format=ModelFormat.API,
        context_window=128_000,
        max_output_tokens=4096,
        supports_vision=True,
    )
    adapter = OpenAICompatAdapter(profile=profile, base_url="https://x", model="gpt-4o")
    payload = adapter._payload(_REQ_WITH_IMAGE, stream=False)
    content = payload["messages"][0]["content"]
    assert isinstance(content, list)
    kinds = [c["type"] for c in content]
    assert kinds == ["text", "image_url"]


def test_openai_payload_text_only_without_attachments() -> None:
    profile = ModelProfile(
        name="m",
        family=ModelFamily.GPT,
        format=ModelFormat.API,
        context_window=128_000,
        max_output_tokens=4096,
        supports_vision=True,
    )
    adapter = OpenAICompatAdapter(profile=profile, base_url="https://x", model="gpt-4o")
    payload = adapter._payload(GenerationRequest(prompt="hi"), stream=False)
    assert payload["messages"][0]["content"] == "hi"

from __future__ import annotations

import base64
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from prompt_autoimprove.domain.prompt import Modality

if TYPE_CHECKING:
    from collections.abc import Iterable

    from prompt_autoimprove.domain.prompt import PromptAttachment

_IMAGE_MODALITIES = (Modality.IMAGE,)


def _is_image(att: PromptAttachment) -> bool:
    return att.modality in _IMAGE_MODALITIES or att.mime_type.startswith("image/")


def _read_file_uri(uri: str) -> bytes:
    parsed = urlparse(uri)
    return Path(parsed.path).read_bytes()


def _data_uri_parts(uri: str) -> tuple[str, str]:
    head, _, b64 = uri.partition(",")
    media_type = head.removeprefix("data:").split(";")[0] or "application/octet-stream"
    return media_type, b64


def to_anthropic_blocks(
    attachments: Iterable[PromptAttachment],
) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    for att in attachments:
        if not _is_image(att):
            continue
        scheme = urlparse(att.uri).scheme
        if scheme in ("http", "https"):
            blocks.append({"type": "image", "source": {"type": "url", "url": att.uri}})
        elif scheme == "data":
            media_type, data = _data_uri_parts(att.uri)
            blocks.append(
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": data},
                }
            )
        elif scheme == "file":
            data = base64.b64encode(_read_file_uri(att.uri)).decode("ascii")
            blocks.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": att.mime_type or "image/png",
                        "data": data,
                    },
                }
            )
    return blocks


def to_openai_blocks(
    attachments: Iterable[PromptAttachment],
) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    for att in attachments:
        if not _is_image(att):
            continue
        scheme = urlparse(att.uri).scheme
        if scheme in ("http", "https", "data"):
            url = att.uri
        elif scheme == "file":
            data = base64.b64encode(_read_file_uri(att.uri)).decode("ascii")
            url = f"data:{att.mime_type or 'image/png'};base64,{data}"
        else:
            continue
        blocks.append({"type": "image_url", "image_url": {"url": url}})
    return blocks

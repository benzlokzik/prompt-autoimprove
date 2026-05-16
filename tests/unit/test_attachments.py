import base64
from pathlib import Path

from prompt_autoimprove.adapters._attachments import to_anthropic_blocks, to_openai_blocks
from prompt_autoimprove.domain.prompt import Modality, PromptAttachment


def _att(uri: str, mime: str = "image/png") -> PromptAttachment:
    return PromptAttachment(modality=Modality.IMAGE, uri=uri, mime_type=mime)


def test_anthropic_url_block() -> None:
    blocks = to_anthropic_blocks([_att("https://example.com/cat.png")])
    assert blocks == [
        {"type": "image", "source": {"type": "url", "url": "https://example.com/cat.png"}}
    ]


def test_anthropic_data_uri_block() -> None:
    payload = base64.b64encode(b"PNG-bytes").decode()
    blocks = to_anthropic_blocks([_att(f"data:image/png;base64,{payload}")])
    assert blocks == [
        {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": payload},
        }
    ]


def test_anthropic_file_uri_reads_and_base64_encodes(tmp_path: Path) -> None:
    img = tmp_path / "pixel.png"
    raw = b"\x89PNG\r\n\x1a\n-payload"
    img.write_bytes(raw)
    blocks = to_anthropic_blocks([_att(f"file://{img}", mime="image/png")])
    assert blocks[0]["source"]["data"] == base64.b64encode(raw).decode()
    assert blocks[0]["source"]["media_type"] == "image/png"


def test_anthropic_skips_non_image_attachment() -> None:
    pdf = PromptAttachment(
        modality=Modality.MIXED, uri="https://x/y.pdf", mime_type="application/pdf"
    )
    assert to_anthropic_blocks([pdf]) == []


def test_openai_url_block() -> None:
    blocks = to_openai_blocks([_att("https://example.com/cat.png")])
    assert blocks == [{"type": "image_url", "image_url": {"url": "https://example.com/cat.png"}}]


def test_openai_file_inlines_as_data_uri(tmp_path: Path) -> None:
    img = tmp_path / "px.jpg"
    raw = b"\xff\xd8jpeg-bytes"
    img.write_bytes(raw)
    blocks = to_openai_blocks([_att(f"file://{img}", mime="image/jpeg")])
    expected = f"data:image/jpeg;base64,{base64.b64encode(raw).decode()}"
    assert blocks == [{"type": "image_url", "image_url": {"url": expected}}]

from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import NanoBanana2EditConfig


def test_nano_banana_2_edit_config_accepts_remote_and_local_style_image_urls() -> None:
    config = NanoBanana2EditConfig(
        app_id="fal-ai/nano-banana-2/edit",
        prompt="make the scene look like golden hour",
        image_urls=[
            "https://storage.googleapis.com/falserverless/example_inputs/nano-banana-edit-input.png",
            "./fixtures/local-input.png",
        ],
    )

    assert config.image_urls == [
        "https://storage.googleapis.com/falserverless/example_inputs/nano-banana-edit-input.png",
        "./fixtures/local-input.png",
    ]
    assert config.system_prompt == ""


def test_nano_banana_2_edit_config_accepts_system_prompt() -> None:
    config = NanoBanana2EditConfig(
        app_id="fal-ai/nano-banana-2/edit",
        prompt="make the scene look like golden hour",
        image_urls=[
            "https://storage.googleapis.com/falserverless/example_inputs/nano-banana-edit-input.png",
        ],
        system_prompt="Keep the source composition and use a cinematic color grade.",
    )

    assert config.system_prompt == ("Keep the source composition and use a cinematic color grade.")


@pytest.mark.parametrize(
    ("field_name", "url"),
    [
        ("video_url", "https://example.com/context.mp4"),
        ("audio_url", "https://example.com/context.mp3"),
        ("pdf_url", "https://example.com/context.pdf"),
    ],
)
def test_nano_banana_2_edit_config_accepts_non_image_context_without_image_urls(
    field_name: str,
    url: str,
) -> None:
    config = NanoBanana2EditConfig(
        app_id="fal-ai/nano-banana-2/edit",
        prompt="use this context to edit the requested image",
        **{field_name: url},
    )

    assert config.image_urls is None
    assert getattr(config, field_name) == url


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {"app_id": "fal-ai/nano-banana-2/edit", "prompt": "edit this"},
            "image_urls, video_url, audio_url, or pdf_url",
        ),
        (
            {
                "app_id": "fal-ai/nano-banana-2/edit",
                "prompt": "edit this",
                "image_urls": [],
            },
            "image_urls",
        ),
    ],
)
def test_nano_banana_2_edit_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        NanoBanana2EditConfig(**payload)

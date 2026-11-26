from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Veo31ImageToVideoConfig


def test_veo3_1_image_to_video_accepts_schema_defaults() -> None:
    config = Veo31ImageToVideoConfig(
        app_id="fal-ai/veo3.1/image-to-video",
        prompt="The subject turns toward the camera.",
        image_url="https://example.com/input.png",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/veo3.1/image-to-video",
        "prompt": "The subject turns toward the camera.",
        "aspect_ratio": "auto",
        "duration": "8s",
        "negative_prompt": None,
        "resolution": "720p",
        "generate_audio": True,
        "seed": None,
        "auto_fix": False,
        "safety_tolerance": "4",
        "image_url": "https://example.com/input.png",
    }


def test_veo3_1_image_to_video_accepts_all_fields() -> None:
    config = Veo31ImageToVideoConfig(
        app_id="fal-ai/veo3.1/image-to-video",
        prompt="Animate the product with a slow dolly-in.",
        aspect_ratio="16:9",
        duration="4s",
        negative_prompt="low detail",
        resolution="4k",
        generate_audio=False,
        seed=42,
        auto_fix=True,
        safety_tolerance="5",
        image_url="https://example.com/product.png",
    )

    assert config.aspect_ratio == "16:9"
    assert config.duration == "4s"
    assert config.negative_prompt == "low detail"
    assert config.resolution == "4k"
    assert config.generate_audio is False
    assert config.seed == 42
    assert config.auto_fix is True
    assert config.safety_tolerance == "5"


@pytest.mark.parametrize("aspect_ratio", ["auto", "16:9", "9:16"])
def test_veo3_1_image_to_video_accepts_aspect_ratio_values(aspect_ratio: str) -> None:
    config = Veo31ImageToVideoConfig(
        app_id="fal-ai/veo3.1/image-to-video",
        prompt="Animate the subject.",
        image_url="https://example.com/input.png",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "fal-ai/veo3.1/image-to-video",
                "prompt": "Animate the subject.",
            },
            "image_url",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1/image-to-video",
                "image_url": "https://example.com/input.png",
            },
            "prompt",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1/image-to-video",
                "prompt": "Animate the subject.",
                "image_url": "https://example.com/input.png",
                "aspect_ratio": "1:1",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1/image-to-video",
                "prompt": "Animate the subject.",
                "image_url": "https://example.com/input.png",
                "duration": "10s",
            },
            "duration",
        ),
    ],
)
def test_veo3_1_image_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Veo31ImageToVideoConfig.model_validate(payload)

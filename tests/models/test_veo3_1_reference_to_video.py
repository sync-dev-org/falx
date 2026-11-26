from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Veo31ReferenceToVideoConfig


def test_veo3_1_reference_to_video_accepts_schema_defaults() -> None:
    config = Veo31ReferenceToVideoConfig(
        app_id="fal-ai/veo3.1/reference-to-video",
        prompt="Animate the references into a cohesive product shot.",
        image_urls=[
            "https://example.com/ref-1.png",
            "https://example.com/ref-2.png",
        ],
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/veo3.1/reference-to-video",
        "prompt": "Animate the references into a cohesive product shot.",
        "aspect_ratio": "16:9",
        "duration": "8s",
        "resolution": "720p",
        "generate_audio": True,
        "auto_fix": False,
        "safety_tolerance": "4",
        "image_urls": [
            "https://example.com/ref-1.png",
            "https://example.com/ref-2.png",
        ],
    }


def test_veo3_1_reference_to_video_accepts_all_fields() -> None:
    config = Veo31ReferenceToVideoConfig(
        app_id="fal-ai/veo3.1/reference-to-video",
        prompt="Use the references to preserve the character identity.",
        aspect_ratio="9:16",
        duration="12s",
        resolution="4k",
        generate_audio=False,
        auto_fix=True,
        safety_tolerance="1",
        image_urls=["https://example.com/ref.png"],
    )

    assert config.aspect_ratio == "9:16"
    assert config.duration == "12s"
    assert config.resolution == "4k"
    assert config.generate_audio is False
    assert config.auto_fix is True
    assert config.safety_tolerance == "1"


@pytest.mark.parametrize("duration", ["4s", "8s", "12s", "custom-duration"])
def test_veo3_1_reference_to_video_accepts_duration_string(duration: str) -> None:
    config = Veo31ReferenceToVideoConfig(
        app_id="fal-ai/veo3.1/reference-to-video",
        prompt="Animate the references.",
        image_urls=["https://example.com/ref.png"],
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "fal-ai/veo3.1/reference-to-video",
                "image_urls": ["https://example.com/ref.png"],
            },
            "prompt",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1/reference-to-video",
                "prompt": "Animate the references.",
            },
            "image_urls",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1/reference-to-video",
                "prompt": "Animate the references.",
                "image_urls": ["https://example.com/ref.png"],
                "aspect_ratio": "auto",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1/reference-to-video",
                "prompt": "Animate the references.",
                "image_urls": ["https://example.com/ref.png"],
                "negative_prompt": "blur",
            },
            "negative_prompt",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1/reference-to-video",
                "prompt": "Animate the references.",
                "image_urls": ["https://example.com/ref.png"],
                "seed": 42,
            },
            "seed",
        ),
    ],
)
def test_veo3_1_reference_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Veo31ReferenceToVideoConfig.model_validate(payload)

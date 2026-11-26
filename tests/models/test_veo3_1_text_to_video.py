from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Veo31TextToVideoConfig


def test_veo3_1_text_to_video_accepts_schema_defaults() -> None:
    config = Veo31TextToVideoConfig(
        app_id="fal-ai/veo3.1",
        prompt="A cinematic street interview at sunset.",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/veo3.1",
        "prompt": "A cinematic street interview at sunset.",
        "aspect_ratio": "16:9",
        "duration": "8s",
        "negative_prompt": None,
        "resolution": "720p",
        "generate_audio": True,
        "seed": None,
        "auto_fix": True,
        "safety_tolerance": "4",
    }


def test_veo3_1_text_to_video_accepts_all_fields() -> None:
    config = Veo31TextToVideoConfig(
        app_id="fal-ai/veo3.1",
        prompt="A crisp documentary shot of a tram crossing a bridge.",
        aspect_ratio="9:16",
        duration="6s",
        negative_prompt="blur, distortion",
        resolution="1080p",
        generate_audio=False,
        seed=1234,
        auto_fix=False,
        safety_tolerance="6",
    )

    assert config.aspect_ratio == "9:16"
    assert config.duration == "6s"
    assert config.negative_prompt == "blur, distortion"
    assert config.resolution == "1080p"
    assert config.generate_audio is False
    assert config.seed == 1234
    assert config.auto_fix is False
    assert config.safety_tolerance == "6"


@pytest.mark.parametrize("duration", ["4s", "6s", "8s"])
def test_veo3_1_text_to_video_accepts_duration_values(duration: str) -> None:
    config = Veo31TextToVideoConfig(
        app_id="fal-ai/veo3.1",
        prompt="A quiet city park.",
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "fal-ai/veo3.1"}, "prompt"),
        (
            {
                "app_id": "fal-ai/veo3.1",
                "prompt": "A quiet city park.",
                "aspect_ratio": "auto",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1",
                "prompt": "A quiet city park.",
                "duration": "5s",
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1",
                "prompt": "A quiet city park.",
                "resolution": "480p",
            },
            "resolution",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1",
                "prompt": "A quiet city park.",
                "safety_tolerance": "7",
            },
            "safety_tolerance",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1",
                "prompt": "A quiet city park.",
                "image_url": "https://example.com/input.png",
            },
            "image_url",
        ),
    ],
)
def test_veo3_1_text_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Veo31TextToVideoConfig.model_validate(payload)

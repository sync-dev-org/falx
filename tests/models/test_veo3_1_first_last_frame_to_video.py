from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Veo31FirstLastFrameToVideoConfig


def test_veo3_1_first_last_frame_to_video_accepts_schema_defaults() -> None:
    config = Veo31FirstLastFrameToVideoConfig(
        app_id="fal-ai/veo3.1/first-last-frame-to-video",
        prompt="Animate smoothly from the first frame to the last frame.",
        first_frame_url="https://example.com/first.png",
        last_frame_url="https://example.com/last.png",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/veo3.1/first-last-frame-to-video",
        "prompt": "Animate smoothly from the first frame to the last frame.",
        "aspect_ratio": "auto",
        "duration": "8s",
        "negative_prompt": None,
        "resolution": "720p",
        "generate_audio": True,
        "seed": None,
        "auto_fix": False,
        "safety_tolerance": "4",
        "first_frame_url": "https://example.com/first.png",
        "last_frame_url": "https://example.com/last.png",
    }


def test_veo3_1_first_last_frame_to_video_accepts_all_fields() -> None:
    config = Veo31FirstLastFrameToVideoConfig(
        app_id="fal-ai/veo3.1/first-last-frame-to-video",
        prompt="Move from morning to night with a smooth camera arc.",
        aspect_ratio="9:16",
        duration="6s",
        negative_prompt="jitter",
        resolution="1080p",
        generate_audio=False,
        seed=9001,
        auto_fix=True,
        safety_tolerance="2",
        first_frame_url="https://example.com/morning.png",
        last_frame_url="https://example.com/night.png",
    )

    assert config.aspect_ratio == "9:16"
    assert config.duration == "6s"
    assert config.negative_prompt == "jitter"
    assert config.resolution == "1080p"
    assert config.generate_audio is False
    assert config.seed == 9001
    assert config.auto_fix is True
    assert config.safety_tolerance == "2"


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "fal-ai/veo3.1/first-last-frame-to-video",
                "prompt": "Animate between frames.",
                "last_frame_url": "https://example.com/last.png",
            },
            "first_frame_url",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1/first-last-frame-to-video",
                "prompt": "Animate between frames.",
                "first_frame_url": "https://example.com/first.png",
            },
            "last_frame_url",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1/first-last-frame-to-video",
                "prompt": "Animate between frames.",
                "first_frame_url": "https://example.com/first.png",
                "last_frame_url": "https://example.com/last.png",
                "aspect_ratio": "1:1",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "fal-ai/veo3.1/first-last-frame-to-video",
                "prompt": "Animate between frames.",
                "first_frame_url": "https://example.com/first.png",
                "last_frame_url": "https://example.com/last.png",
                "resolution": "2k",
            },
            "resolution",
        ),
    ],
)
def test_veo3_1_first_last_frame_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Veo31FirstLastFrameToVideoConfig.model_validate(payload)

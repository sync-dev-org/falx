from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import ViduQ3TextToVideoConfig


def test_vidu_q3_text_to_video_accepts_schema_defaults() -> None:
    config = ViduQ3TextToVideoConfig(
        app_id="fal-ai/vidu/q3/text-to-video",
        prompt="An astronaut walks through morning fog in a documentary style.",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/vidu/q3/text-to-video",
        "prompt": "An astronaut walks through morning fog in a documentary style.",
        "duration": 5,
        "seed": None,
        "aspect_ratio": "16:9",
        "resolution": "720p",
        "audio": True,
    }


def test_vidu_q3_text_to_video_accepts_all_fields() -> None:
    config = ViduQ3TextToVideoConfig(
        app_id="fal-ai/vidu/q3/text-to-video",
        prompt="A fashion model crosses a rain-soaked street at night.",
        duration=16,
        seed=1234,
        aspect_ratio="4:3",
        resolution="1080p",
        audio=False,
    )

    assert config.duration == 16
    assert config.seed == 1234
    assert config.aspect_ratio == "4:3"
    assert config.resolution == "1080p"
    assert config.audio is False


@pytest.mark.parametrize("aspect_ratio", ["16:9", "9:16", "4:3", "3:4", "1:1"])
def test_vidu_q3_text_to_video_accepts_aspect_ratio_values(aspect_ratio: str) -> None:
    config = ViduQ3TextToVideoConfig(
        app_id="fal-ai/vidu/q3/text-to-video",
        prompt="A quiet city park.",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("resolution", ["360p", "540p", "720p", "1080p"])
def test_vidu_q3_text_to_video_accepts_resolution_values(resolution: str) -> None:
    config = ViduQ3TextToVideoConfig(
        app_id="fal-ai/vidu/q3/text-to-video",
        prompt="A quiet city park.",
        resolution=resolution,
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("duration", [1, 16])
def test_vidu_q3_text_to_video_accepts_duration_boundaries(duration: int) -> None:
    config = ViduQ3TextToVideoConfig(
        app_id="fal-ai/vidu/q3/text-to-video",
        prompt="A quiet city park.",
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "fal-ai/vidu/q3/text-to-video"}, "prompt"),
        (
            {
                "app_id": "fal-ai/vidu/q3/text-to-video",
                "prompt": "x" * 2001,
            },
            "prompt",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/text-to-video",
                "prompt": "A quiet city park.",
                "duration": 0,
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/text-to-video",
                "prompt": "A quiet city park.",
                "duration": 17,
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/text-to-video",
                "prompt": "A quiet city park.",
                "aspect_ratio": "auto",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/text-to-video",
                "prompt": "A quiet city park.",
                "resolution": "4k",
            },
            "resolution",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/text-to-video",
                "prompt": "A quiet city park.",
                "generate_audio": True,
            },
            "generate_audio",
        ),
    ],
)
def test_vidu_q3_text_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        ViduQ3TextToVideoConfig.model_validate(payload)

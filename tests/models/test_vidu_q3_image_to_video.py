from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import ViduQ3ImageToVideoConfig


def test_vidu_q3_image_to_video_accepts_schema_defaults() -> None:
    config = ViduQ3ImageToVideoConfig(
        app_id="fal-ai/vidu/q3/image-to-video",
        image_url="https://example.com/start.png",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/vidu/q3/image-to-video",
        "prompt": "",
        "image_url": "https://example.com/start.png",
        "end_image_url": None,
        "duration": 5,
        "seed": None,
        "resolution": "720p",
        "audio": True,
    }


def test_vidu_q3_image_to_video_accepts_all_fields() -> None:
    config = ViduQ3ImageToVideoConfig(
        app_id="fal-ai/vidu/q3/image-to-video",
        prompt="The product rotates on a polished table.",
        image_url="https://example.com/start.png",
        end_image_url="https://example.com/end.png",
        duration=12,
        seed=42,
        resolution="1080p",
        audio=False,
    )

    assert config.prompt == "The product rotates on a polished table."
    assert config.end_image_url == "https://example.com/end.png"
    assert config.duration == 12
    assert config.seed == 42
    assert config.resolution == "1080p"
    assert config.audio is False


@pytest.mark.parametrize("duration", [1, 16])
def test_vidu_q3_image_to_video_accepts_duration_boundaries(duration: int) -> None:
    config = ViduQ3ImageToVideoConfig(
        app_id="fal-ai/vidu/q3/image-to-video",
        image_url="https://example.com/start.png",
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize("resolution", ["360p", "540p", "720p", "1080p"])
def test_vidu_q3_image_to_video_accepts_resolution_values(resolution: str) -> None:
    config = ViduQ3ImageToVideoConfig(
        app_id="fal-ai/vidu/q3/image-to-video",
        image_url="https://example.com/start.png",
        resolution=resolution,
    )

    assert config.resolution == resolution


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "fal-ai/vidu/q3/image-to-video"}, "image_url"),
        (
            {
                "app_id": "fal-ai/vidu/q3/image-to-video",
                "prompt": "x" * 2001,
                "image_url": "https://example.com/start.png",
            },
            "prompt",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/image-to-video",
                "image_url": "https://example.com/start.png",
                "duration": 0,
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/image-to-video",
                "image_url": "https://example.com/start.png",
                "duration": 17,
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/image-to-video",
                "image_url": "https://example.com/start.png",
                "resolution": "4k",
            },
            "resolution",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/image-to-video",
                "image_url": "https://example.com/start.png",
                "end_image_url": "https://example.com/end.png",
                "resolution": "360p",
            },
            "360p",
        ),
    ],
)
def test_vidu_q3_image_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        ViduQ3ImageToVideoConfig.model_validate(payload)

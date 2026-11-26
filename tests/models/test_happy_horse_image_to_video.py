from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import HappyHorseImageToVideoConfig


def test_happy_horse_image_to_video_config_accepts_minimal_required_fields() -> None:
    config = HappyHorseImageToVideoConfig(
        app_id="alibaba/happy-horse/image-to-video",
        image_url="https://example.com/start.png",
    )

    assert config.image_url == "https://example.com/start.png"
    assert config.prompt is None
    assert config.resolution == "1080p"
    assert config.duration == 5
    assert config.seed is None
    assert config.enable_safety_checker is True


def test_happy_horse_image_to_video_config_accepts_all_fields() -> None:
    config = HappyHorseImageToVideoConfig(
        app_id="alibaba/happy-horse/image-to-video",
        image_url="https://example.com/start.webp",
        prompt="Bring the scene in the image to life.",
        resolution="720p",
        duration=3,
        seed=42,
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": "alibaba/happy-horse/image-to-video",
        "image_url": "https://example.com/start.webp",
        "prompt": "Bring the scene in the image to life.",
        "resolution": "720p",
        "duration": 3,
        "seed": 42,
        "enable_safety_checker": False,
    }


@pytest.mark.parametrize("resolution", ["720p", "1080p"])
def test_happy_horse_image_to_video_config_accepts_resolution_enum(
    resolution: str,
) -> None:
    config = HappyHorseImageToVideoConfig.model_validate(
        {
            "app_id": "alibaba/happy-horse/image-to-video",
            "image_url": "https://example.com/start.jpg",
            "resolution": resolution,
        }
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("duration", range(3, 16))
def test_happy_horse_image_to_video_config_accepts_duration_enum(duration: int) -> None:
    config = HappyHorseImageToVideoConfig.model_validate(
        {
            "app_id": "alibaba/happy-horse/image-to-video",
            "image_url": "https://example.com/start.jpg",
            "duration": duration,
        }
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "alibaba/happy-horse/image-to-video"}, "image_url"),
        (
            {
                "app_id": "alibaba/happy-horse/image-to-video",
                "image_url": "https://example.com/start.jpg",
                "prompt": "x" * 2501,
            },
            "prompt",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/image-to-video",
                "image_url": "https://example.com/start.jpg",
                "resolution": "480p",
            },
            "resolution",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/image-to-video",
                "image_url": "https://example.com/start.jpg",
                "duration": 2,
            },
            "duration",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/image-to-video",
                "image_url": "https://example.com/start.jpg",
                "duration": 16,
            },
            "duration",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/image-to-video",
                "image_url": "https://example.com/start.jpg",
                "seed": -1,
            },
            "seed",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/image-to-video",
                "image_url": "https://example.com/start.jpg",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_happy_horse_image_to_video_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        HappyHorseImageToVideoConfig.model_validate(payload)

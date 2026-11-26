from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    GrokImagineVideoV15ImageToVideoConfig,
    config_class_for_app_id,
)

APP_ID = "xai/grok-imagine-video/v1.5/image-to-video"


def test_grok_imagine_video_v1_5_image_to_video_accepts_schema_defaults() -> None:
    config = GrokImagineVideoV15ImageToVideoConfig(
        app_id=APP_ID,
        prompt="The subject slowly turns toward the camera.",
        image_url="https://example.com/source.png",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "The subject slowly turns toward the camera.",
        "image_url": "https://example.com/source.png",
        "duration": 6,
        "resolution": "720p",
    }


def test_grok_imagine_video_v1_5_image_to_video_accepts_all_fields() -> None:
    config = GrokImagineVideoV15ImageToVideoConfig(
        app_id=APP_ID,
        prompt="The subject slowly turns toward the camera.",
        image_url="https://example.com/source.png",
        duration=15,
        resolution="1080p",
    )

    assert config.duration == 15
    assert config.resolution == "1080p"


@pytest.mark.parametrize("resolution", ["480p", "720p", "1080p"])
@pytest.mark.parametrize("duration", [1, 15])
def test_grok_imagine_video_v1_5_image_to_video_accepts_enums_and_boundaries(
    resolution: str,
    duration: int,
) -> None:
    config = GrokImagineVideoV15ImageToVideoConfig(
        app_id=APP_ID,
        prompt="Animate the subject.",
        image_url="https://example.com/source.png",
        resolution=resolution,
        duration=duration,
    )

    assert config.resolution == resolution
    assert config.duration == duration


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"image_url": "https://example.com/source.png"}, "prompt"),
        ({"prompt": "Animate the subject."}, "image_url"),
        (
            {
                "prompt": "x" * 4097,
                "image_url": "https://example.com/source.png",
            },
            "prompt",
        ),
        (
            {
                "prompt": "Animate the subject.",
                "image_url": "https://example.com/source.png",
                "resolution": "4k",
            },
            "resolution",
        ),
        (
            {
                "prompt": "Animate the subject.",
                "image_url": "https://example.com/source.png",
                "duration": 0,
            },
            "duration",
        ),
        (
            {
                "prompt": "Animate the subject.",
                "image_url": "https://example.com/source.png",
                "aspect_ratio": "16:9",
            },
            "aspect_ratio",
        ),
        (
            {
                "prompt": "Animate the subject.",
                "image_url": "https://example.com/source.png",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_grok_imagine_video_v1_5_image_to_video_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        GrokImagineVideoV15ImageToVideoConfig.model_validate(
            {"app_id": APP_ID, **parameters}
        )


def test_grok_imagine_video_v1_5_image_to_video_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is GrokImagineVideoV15ImageToVideoConfig
    assert GrokImagineVideoV15ImageToVideoConfig.random_seed_field is None

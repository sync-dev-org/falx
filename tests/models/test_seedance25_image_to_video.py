from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    Seedance25ImageToVideoConfig,
    validate_parameters,
)

APP_ID = "bytedance/seedance-2.5/image-to-video"
DOCUMENTED_DURATIONS = ["auto", *(str(value) for value in range(4, 31))]


def test_seedance25_image_to_video_accepts_documented_defaults() -> None:
    config = Seedance25ImageToVideoConfig(
        app_id=APP_ID,
        prompt="The subject turns toward the camera as rain begins.",
        image_url="https://example.com/start.webp",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "The subject turns toward the camera as rain begins.",
        "image_url": "https://example.com/start.webp",
        "end_image_url": None,
        "resolution": "720p",
        "duration": "auto",
        "aspect_ratio": "auto",
        "generate_audio": True,
        "bitrate_mode": "standard",
        "codec": "auto",
        "output_format": "mp4",
        "draft": False,
        "return_last_frame": False,
        "end_user_id": None,
    }


def test_seedance25_image_to_video_accepts_all_documented_fields() -> None:
    config = Seedance25ImageToVideoConfig(
        app_id=APP_ID,
        prompt="Move from the opening frame to the closing frame in one shot.",
        image_url="https://example.com/start.png",
        end_image_url="https://example.com/end.jpg",
        resolution="1080p",
        duration="30",
        aspect_ratio="auto",
        generate_audio=False,
        bitrate_mode="high",
        end_user_id="user-123",
    )

    assert config.end_image_url == "https://example.com/end.jpg"
    assert config.duration == "30"
    assert config.resolution == "1080p"
    assert config.bitrate_mode == "high"


@pytest.mark.parametrize("duration", DOCUMENTED_DURATIONS)
def test_seedance25_image_to_video_accepts_duration_string_enum(duration: str) -> None:
    config = Seedance25ImageToVideoConfig(
        app_id=APP_ID,
        prompt="Animate the still image.",
        image_url="https://example.com/start.png",
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 4),
        ("duration", "3"),
        ("duration", "31"),
        ("aspect_ratio", "16:9"),
        ("bitrate_mode", "lossless"),
        ("resolution", "8k"),
    ],
)
def test_seedance25_image_to_video_rejects_undocumented_enum_values(
    field: str,
    value: object,
) -> None:
    payload: dict[str, object] = {
        "app_id": APP_ID,
        "prompt": "Animate the still image.",
        "image_url": "https://example.com/start.png",
        field: value,
    }

    with pytest.raises(ValidationError, match=field):
        Seedance25ImageToVideoConfig.model_validate(payload)


@pytest.mark.parametrize("missing_field", ["image_url"])
def test_seedance25_image_to_video_requires_documented_fields(missing_field: str) -> None:
    payload = {
        "app_id": APP_ID,
        "prompt": "Animate the still image.",
        "image_url": "https://example.com/start.png",
    }
    del payload[missing_field]

    with pytest.raises(ValidationError, match=missing_field):
        Seedance25ImageToVideoConfig.model_validate(payload)


def test_seedance25_image_to_video_describes_image_media_constraints() -> None:
    description = Seedance25ImageToVideoConfig.model_fields["image_url"].description

    assert description is not None
    assert "JPEG, PNG, WebP" in description
    assert "Max 30 MB" in description


def test_seedance25_image_to_video_is_registered() -> None:
    validated = validate_parameters(
        APP_ID,
        {
            "prompt": "Animate the still image.",
            "image_url": "https://example.com/start.png",
        },
    )

    assert APP_ID in SUPPORTED_APP_IDS
    assert isinstance(validated, Seedance25ImageToVideoConfig)

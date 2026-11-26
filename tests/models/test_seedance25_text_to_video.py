from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    Seedance25TextToVideoConfig,
    validate_parameters,
)

APP_ID = "bytedance/seedance-2.5/text-to-video"
DOCUMENTED_DURATIONS = ["auto", *(str(value) for value in range(4, 31))]


def test_seedance25_text_to_video_accepts_documented_defaults() -> None:
    config = Seedance25TextToVideoConfig(
        app_id=APP_ID,
        prompt="A continuous tracking shot through a lantern-lit market.",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A continuous tracking shot through a lantern-lit market.",
        "aspect_ratio": "auto",
        "duration": "auto",
        "bitrate_mode": "standard",
        "end_user_id": None,
        "generate_audio": True,
        "resolution": "720p",
    }


def test_seedance25_text_to_video_accepts_all_documented_fields() -> None:
    config = Seedance25TextToVideoConfig(
        app_id=APP_ID,
        prompt="A wide landscape slowly changes from winter to spring.",
        aspect_ratio="21:9",
        duration="30",
        bitrate_mode="high",
        end_user_id="user-123",
        generate_audio=False,
        resolution="1080p",
    )

    assert config.duration == "30"
    assert config.aspect_ratio == "21:9"
    assert config.bitrate_mode == "high"
    assert config.end_user_id == "user-123"
    assert config.generate_audio is False
    assert config.resolution == "1080p"


@pytest.mark.parametrize("duration", DOCUMENTED_DURATIONS)
def test_seedance25_text_to_video_accepts_duration_string_enum(duration: str) -> None:
    config = Seedance25TextToVideoConfig(
        app_id=APP_ID,
        prompt="A single-shot dance performance.",
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 4),
        ("duration", "3"),
        ("duration", "31"),
        ("aspect_ratio", "2:1"),
        ("bitrate_mode", "lossless"),
        ("resolution", "4k"),
    ],
)
def test_seedance25_text_to_video_rejects_undocumented_enum_values(
    field: str,
    value: object,
) -> None:
    payload: dict[str, object] = {
        "app_id": APP_ID,
        "prompt": "A single-shot dance performance.",
        field: value,
    }

    with pytest.raises(ValidationError, match=field):
        Seedance25TextToVideoConfig.model_validate(payload)


def test_seedance25_text_to_video_requires_prompt() -> None:
    with pytest.raises(ValidationError, match="prompt"):
        Seedance25TextToVideoConfig.model_validate({"app_id": APP_ID})


def test_seedance25_text_to_video_is_registered() -> None:
    validated = validate_parameters(
        APP_ID,
        {"prompt": "A camera circles a sculpture as the light changes."},
    )

    assert APP_ID in SUPPORTED_APP_IDS
    assert isinstance(validated, Seedance25TextToVideoConfig)

from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    KlingVideoO34kVideoToVideoReferenceConfig,
    config_class_for_app_id,
)

APP_ID = "fal-ai/kling-video/o3/4k/video-to-video/reference"


def test_kling_o3_4k_video_to_video_reference_accepts_schema_defaults() -> None:
    config = KlingVideoO34kVideoToVideoReferenceConfig(
        app_id=APP_ID,
        prompt="Follow the watercolor style of the reference.",
        video_url="https://example.com/reference.mp4",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "enable_safety_checker": True,
        "prompt": "Follow the watercolor style of the reference.",
        "video_url": "https://example.com/reference.mp4",
        "shot_type": "customize",
        "elements": None,
        "keep_audio": True,
        "image_urls": None,
        "aspect_ratio": "auto",
        "duration": None,
    }


def test_kling_o3_4k_video_to_video_reference_accepts_all_fields() -> None:
    config = KlingVideoO34kVideoToVideoReferenceConfig(
        app_id=APP_ID,
        prompt="Integrate @Element1 and follow @Image1 styling.",
        video_url="https://example.com/reference.mov",
        elements=[{"frontal_image_url": "https://example.com/front.png"}],
        keep_audio=False,
        image_urls=["https://example.com/style.png"],
        aspect_ratio="9:16",
        duration="15",
    )

    assert config.keep_audio is False
    assert config.aspect_ratio == "9:16"
    assert config.duration == "15"


@pytest.mark.parametrize("aspect_ratio", ["auto", "16:9", "9:16", "1:1"])
def test_kling_o3_4k_video_to_video_reference_accepts_aspect_ratio_enum(
    aspect_ratio: str,
) -> None:
    config = KlingVideoO34kVideoToVideoReferenceConfig(
        app_id=APP_ID,
        prompt="Restyle the clip.",
        video_url="https://example.com/reference.mp4",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("duration", [None, *[str(value) for value in range(3, 16)]])
def test_kling_o3_4k_video_to_video_reference_accepts_duration_enum(
    duration: str | None,
) -> None:
    config = KlingVideoO34kVideoToVideoReferenceConfig(
        app_id=APP_ID,
        prompt="Restyle the clip.",
        video_url="https://example.com/reference.mp4",
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"video_url": "https://example.com/reference.mp4"}, "prompt"),
        ({"prompt": "Restyle the clip."}, "video_url"),
        (
            {
                "prompt": "Restyle the clip.",
                "video_url": "https://example.com/reference.mp4",
                "aspect_ratio": "4:3",
            },
            "aspect_ratio",
        ),
        (
            {
                "prompt": "Restyle the clip.",
                "video_url": "https://example.com/reference.mp4",
                "duration": "2",
            },
            "duration",
        ),
        (
            {
                "prompt": "Restyle the clip.",
                "video_url": "https://example.com/reference.mp4",
                "duration": 3,
            },
            "duration",
        ),
        (
            {
                "prompt": "Restyle the clip.",
                "video_url": "https://example.com/reference.mp4",
                "elements": [{"frontal_image_url": "https://example.com/front.png"}],
                "image_urls": [f"https://example.com/ref-{index}.png" for index in range(4)],
            },
            "Maximum 4 total",
        ),
        (
            {
                "prompt": "Restyle the clip.",
                "video_url": "https://example.com/reference.mp4",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_kling_o3_4k_video_to_video_reference_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        KlingVideoO34kVideoToVideoReferenceConfig.model_validate({"app_id": APP_ID, **parameters})


def test_kling_o3_4k_video_to_video_reference_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is KlingVideoO34kVideoToVideoReferenceConfig
    assert KlingVideoO34kVideoToVideoReferenceConfig.random_seed_field is None

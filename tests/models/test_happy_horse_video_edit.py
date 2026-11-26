from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import HappyHorseVideoEditConfig


def test_happy_horse_video_edit_config_accepts_minimal_required_fields() -> None:
    config = HappyHorseVideoEditConfig(
        app_id="alibaba/happy-horse/video-edit",
        video_url="https://example.com/source.mp4",
        prompt="Recolor the sky to a deep purple sunset.",
    )

    assert config.video_url == "https://example.com/source.mp4"
    assert config.prompt == "Recolor the sky to a deep purple sunset."
    assert config.reference_image_urls is None
    assert config.resolution == "1080p"
    assert config.audio_setting == "auto"
    assert config.seed is None
    assert config.enable_safety_checker is True


def test_happy_horse_video_edit_config_accepts_all_fields() -> None:
    config = HappyHorseVideoEditConfig(
        app_id="alibaba/happy-horse/video-edit",
        video_url="https://example.com/source.mov",
        prompt="Replace the jacket with the style shown in @Image1.",
        reference_image_urls=["https://example.com/jacket.png"],
        resolution="720p",
        audio_setting="origin",
        seed=42,
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": "alibaba/happy-horse/video-edit",
        "video_url": "https://example.com/source.mov",
        "prompt": "Replace the jacket with the style shown in @Image1.",
        "reference_image_urls": ["https://example.com/jacket.png"],
        "resolution": "720p",
        "audio_setting": "origin",
        "seed": 42,
        "enable_safety_checker": False,
    }


def test_happy_horse_video_edit_config_accepts_reference_image_boundaries() -> None:
    config = HappyHorseVideoEditConfig.model_validate(
        {
            "app_id": "alibaba/happy-horse/video-edit",
            "video_url": "https://example.com/source.mp4",
            "prompt": "Use @Image1 through @Image5 as edit references.",
            "reference_image_urls": [
                f"https://example.com/reference-{index}.png" for index in range(1, 6)
            ],
        }
    )

    assert len(config.reference_image_urls or []) == 5


@pytest.mark.parametrize("audio_setting", ["auto", "origin"])
def test_happy_horse_video_edit_config_accepts_audio_setting_enum(
    audio_setting: str,
) -> None:
    config = HappyHorseVideoEditConfig.model_validate(
        {
            "app_id": "alibaba/happy-horse/video-edit",
            "video_url": "https://example.com/source.mp4",
            "prompt": "Adjust the lighting.",
            "audio_setting": audio_setting,
        }
    )

    assert config.audio_setting == audio_setting


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "alibaba/happy-horse/video-edit", "prompt": "Edit it."}, "video_url"),
        (
            {
                "app_id": "alibaba/happy-horse/video-edit",
                "video_url": "https://example.com/source.mp4",
            },
            "prompt",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/video-edit",
                "video_url": "https://example.com/source.mp4",
                "prompt": "x" * 2501,
            },
            "prompt",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/video-edit",
                "video_url": "https://example.com/source.mp4",
                "prompt": "Use too many references.",
                "reference_image_urls": [
                    f"https://example.com/reference-{index}.png" for index in range(6)
                ],
            },
            "reference_image_urls",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/video-edit",
                "video_url": "https://example.com/source.mp4",
                "prompt": "Use @Image2 for the jacket.",
                "reference_image_urls": ["https://example.com/reference-1.png"],
            },
            "@Image2",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/video-edit",
                "video_url": "https://example.com/source.mp4",
                "prompt": "Use @Image6 for the jacket.",
                "reference_image_urls": [
                    f"https://example.com/reference-{index}.png" for index in range(1, 6)
                ],
            },
            "@Image6",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/video-edit",
                "video_url": "https://example.com/source.mp4",
                "prompt": "Adjust the lighting.",
                "resolution": "480p",
            },
            "resolution",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/video-edit",
                "video_url": "https://example.com/source.mp4",
                "prompt": "Adjust the lighting.",
                "audio_setting": "regenerate",
            },
            "audio_setting",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/video-edit",
                "video_url": "https://example.com/source.mp4",
                "prompt": "Adjust the lighting.",
                "seed": -1,
            },
            "seed",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/video-edit",
                "video_url": "https://example.com/source.mp4",
                "prompt": "Adjust the lighting.",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_happy_horse_video_edit_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        HappyHorseVideoEditConfig.model_validate(payload)

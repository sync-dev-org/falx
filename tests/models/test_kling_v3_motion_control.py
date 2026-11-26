from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import KlingV3ImageElementInput, KlingVideoV3ProMotionControlConfig


def test_kling_v3_motion_control_config_accepts_minimal_required_fields() -> None:
    config = KlingVideoV3ProMotionControlConfig(
        app_id="fal-ai/kling-video/v3/pro/motion-control",
        image_url="https://example.com/character.png",
        video_url="https://example.com/motion.mp4",
        character_orientation="image",
    )

    assert config.prompt is None
    assert config.image_url == "https://example.com/character.png"
    assert config.video_url == "https://example.com/motion.mp4"
    assert config.character_orientation == "image"
    assert config.elements is None
    assert config.keep_original_sound is True


def test_kling_v3_motion_control_config_accepts_all_fields() -> None:
    config = KlingVideoV3ProMotionControlConfig(
        app_id="fal-ai/kling-video/v3/pro/motion-control",
        prompt="Make the character perform the same dance as the reference video.",
        image_url="https://example.com/character.webp",
        video_url="https://example.com/motion.mp4",
        character_orientation="video",
        elements=[
            KlingV3ImageElementInput(
                frontal_image_url="https://example.com/face-front.png",
                reference_image_urls=[
                    "https://example.com/face-left.png",
                    "https://example.com/face-right.png",
                ],
            )
        ],
        keep_original_sound=False,
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/kling-video/v3/pro/motion-control",
        "enable_safety_checker": True,
        "prompt": "Make the character perform the same dance as the reference video.",
        "image_url": "https://example.com/character.webp",
        "video_url": "https://example.com/motion.mp4",
        "character_orientation": "video",
        "elements": [
            {
                "frontal_image_url": "https://example.com/face-front.png",
                "reference_image_urls": [
                    "https://example.com/face-left.png",
                    "https://example.com/face-right.png",
                ],
            }
        ],
        "keep_original_sound": False,
    }


@pytest.mark.parametrize("character_orientation", ["image", "video"])
def test_kling_v3_motion_control_config_accepts_character_orientation_enum(
    character_orientation: str,
) -> None:
    config = KlingVideoV3ProMotionControlConfig.model_validate(
        {
            "app_id": "fal-ai/kling-video/v3/pro/motion-control",
            "image_url": "https://example.com/character.jpg",
            "video_url": "https://example.com/motion.mp4",
            "character_orientation": character_orientation,
        }
    )

    assert config.character_orientation == character_orientation


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "video_url": "https://example.com/motion.mp4",
                "character_orientation": "image",
            },
            "image_url",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "image_url": "https://example.com/character.jpg",
                "character_orientation": "image",
            },
            "video_url",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "image_url": "https://example.com/character.jpg",
                "video_url": "https://example.com/motion.mp4",
            },
            "character_orientation",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "image_url": "https://example.com/character.jpg",
                "video_url": "https://example.com/motion.mp4",
                "character_orientation": "front",
            },
            "character_orientation",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "image_url": "https://example.com/character.jpg",
                "video_url": "https://example.com/motion.mp4",
                "character_orientation": "image",
                "unexpected": True,
            },
            "unexpected",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "prompt": "x" * 2501,
                "image_url": "https://example.com/character.jpg",
                "video_url": "https://example.com/motion.mp4",
                "character_orientation": "image",
            },
            "prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "image_url": "https://example.com/character.jpg",
                "video_url": "https://example.com/motion.mp4",
                "character_orientation": "video",
                "elements": [
                    {"frontal_image_url": "https://example.com/face-1.png"},
                    {"frontal_image_url": "https://example.com/face-2.png"},
                ],
            },
            "elements",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "image_url": "https://example.com/character.jpg",
                "video_url": "https://example.com/motion.mp4",
                "character_orientation": "image",
                "elements": [
                    {"frontal_image_url": "https://example.com/face-front.png"},
                ],
            },
            "character_orientation",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "image_url": "https://example.com/character.jpg",
                "video_url": "https://example.com/motion.mp4",
                "character_orientation": "video",
                "elements": [{}],
            },
            "frontal_image_url or reference_image_urls",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "image_url": "https://example.com/character.jpg",
                "video_url": "https://example.com/motion.mp4",
                "character_orientation": "video",
                "elements": [{"reference_image_urls": []}],
            },
            "reference_image_urls",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/motion-control",
                "image_url": "https://example.com/character.jpg",
                "video_url": "https://example.com/motion.mp4",
                "character_orientation": "video",
                "elements": [
                    {
                        "reference_image_urls": [
                            "https://example.com/face-1.png",
                            "https://example.com/face-2.png",
                            "https://example.com/face-3.png",
                            "https://example.com/face-4.png",
                        ]
                    }
                ],
            },
            "reference_image_urls",
        ),
    ],
)
def test_kling_v3_motion_control_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        KlingVideoV3ProMotionControlConfig.model_validate(payload)

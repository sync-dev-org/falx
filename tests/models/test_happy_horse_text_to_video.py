from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import HappyHorseTextToVideoConfig


def test_happy_horse_text_to_video_config_accepts_minimal_required_fields() -> None:
    config = HappyHorseTextToVideoConfig(
        app_id="alibaba/happy-horse/text-to-video",
        prompt="A little girl walking on the road at sunset.",
    )

    assert config.prompt == "A little girl walking on the road at sunset."
    assert config.aspect_ratio == "16:9"
    assert config.resolution == "1080p"
    assert config.duration == 5
    assert config.seed is None
    assert config.enable_safety_checker is True


def test_happy_horse_text_to_video_config_accepts_all_fields() -> None:
    config = HappyHorseTextToVideoConfig(
        app_id="alibaba/happy-horse/text-to-video",
        prompt="A cinematic aerial shot of a quiet harbor at dawn.",
        aspect_ratio="9:16",
        resolution="720p",
        duration=15,
        seed=2_147_483_647,
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": "alibaba/happy-horse/text-to-video",
        "prompt": "A cinematic aerial shot of a quiet harbor at dawn.",
        "aspect_ratio": "9:16",
        "resolution": "720p",
        "duration": 15,
        "seed": 2_147_483_647,
        "enable_safety_checker": False,
    }


@pytest.mark.parametrize("prompt_length", [1, 2500])
def test_happy_horse_text_to_video_config_accepts_prompt_length_boundaries(
    prompt_length: int,
) -> None:
    config = HappyHorseTextToVideoConfig(
        app_id="alibaba/happy-horse/text-to-video",
        prompt="x" * prompt_length,
    )

    assert config.prompt == "x" * prompt_length


@pytest.mark.parametrize("aspect_ratio", ["16:9", "9:16", "1:1", "4:3", "3:4"])
def test_happy_horse_text_to_video_config_accepts_aspect_ratio_enum(
    aspect_ratio: str,
) -> None:
    config = HappyHorseTextToVideoConfig.model_validate(
        {
            "app_id": "alibaba/happy-horse/text-to-video",
            "prompt": "A cinematic city street fills with morning light.",
            "aspect_ratio": aspect_ratio,
        }
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("duration", range(3, 16))
def test_happy_horse_text_to_video_config_accepts_duration_enum(duration: int) -> None:
    config = HappyHorseTextToVideoConfig.model_validate(
        {
            "app_id": "alibaba/happy-horse/text-to-video",
            "prompt": "A dancer moves through a neon-lit rainstorm.",
            "duration": duration,
        }
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "alibaba/happy-horse/text-to-video"}, "prompt"),
        ({"app_id": "alibaba/happy-horse/text-to-video", "prompt": ""}, "prompt"),
        (
            {
                "app_id": "alibaba/happy-horse/text-to-video",
                "prompt": "x" * 2501,
            },
            "prompt",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "aspect_ratio": "21:9",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "resolution": "480p",
            },
            "resolution",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "duration": 2,
            },
            "duration",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "duration": 16,
            },
            "duration",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "seed": -1,
            },
            "seed",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "seed": 2_147_483_648,
            },
            "seed",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_happy_horse_text_to_video_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        HappyHorseTextToVideoConfig.model_validate(payload)

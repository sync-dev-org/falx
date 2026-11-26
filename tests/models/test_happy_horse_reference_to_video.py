from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import HappyHorseReferenceToVideoConfig


def test_happy_horse_reference_to_video_config_accepts_minimal_required_fields() -> None:
    config = HappyHorseReferenceToVideoConfig(
        app_id="alibaba/happy-horse/reference-to-video",
        prompt="A dance battle between character1 and character2.",
        image_urls=[
            "https://example.com/character-1.png",
            "https://example.com/character-2.png",
        ],
    )

    assert config.prompt == "A dance battle between character1 and character2."
    assert config.image_urls == [
        "https://example.com/character-1.png",
        "https://example.com/character-2.png",
    ]
    assert config.aspect_ratio == "16:9"
    assert config.resolution == "1080p"
    assert config.duration == 5
    assert config.seed is None
    assert config.enable_safety_checker is True


def test_happy_horse_reference_to_video_config_accepts_all_fields() -> None:
    config = HappyHorseReferenceToVideoConfig(
        app_id="alibaba/happy-horse/reference-to-video",
        prompt="character1 and character2 perform a synchronized dance routine.",
        image_urls=[
            "https://example.com/character-1.webp",
            "https://example.com/character-2.webp",
        ],
        aspect_ratio="3:4",
        resolution="720p",
        duration=15,
        seed=42,
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": "alibaba/happy-horse/reference-to-video",
        "prompt": "character1 and character2 perform a synchronized dance routine.",
        "image_urls": [
            "https://example.com/character-1.webp",
            "https://example.com/character-2.webp",
        ],
        "aspect_ratio": "3:4",
        "resolution": "720p",
        "duration": 15,
        "seed": 42,
        "enable_safety_checker": False,
    }


def test_happy_horse_reference_to_video_config_accepts_image_url_boundaries() -> None:
    config = HappyHorseReferenceToVideoConfig.model_validate(
        {
            "app_id": "alibaba/happy-horse/reference-to-video",
            "prompt": "Use character1 through character9 in a wide ensemble shot.",
            "image_urls": [f"https://example.com/character-{index}.png" for index in range(1, 10)],
        }
    )

    assert len(config.image_urls) == 9


@pytest.mark.parametrize("prompt_length", [1, 2500])
def test_happy_horse_reference_to_video_config_accepts_prompt_length_boundaries(
    prompt_length: int,
) -> None:
    config = HappyHorseReferenceToVideoConfig(
        app_id="alibaba/happy-horse/reference-to-video",
        prompt="x" * prompt_length,
        image_urls=["https://example.com/character-1.png"],
    )

    assert config.prompt == "x" * prompt_length


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "alibaba/happy-horse/reference-to-video"}, "prompt"),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "",
                "image_urls": ["https://example.com/character-1.png"],
            },
            "prompt",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "Animate character1.",
            },
            "image_urls",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "Animate character1.",
                "image_urls": [],
            },
            "image_urls",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "Animate character1 through character10.",
                "image_urls": [f"https://example.com/character-{index}.png" for index in range(10)],
            },
            "image_urls",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "Animate character3.",
                "image_urls": [
                    "https://example.com/character-1.png",
                    "https://example.com/character-2.png",
                ],
            },
            "character3",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "Animate character10.",
                "image_urls": [f"https://example.com/character-{index}.png" for index in range(9)],
            },
            "character10",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "x" * 2501,
                "image_urls": ["https://example.com/character-1.png"],
            },
            "prompt",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "Animate character1.",
                "image_urls": ["https://example.com/character-1.png"],
                "aspect_ratio": "21:9",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "Animate character1.",
                "image_urls": ["https://example.com/character-1.png"],
                "duration": 16,
            },
            "duration",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "Animate character1.",
                "image_urls": ["https://example.com/character-1.png"],
                "seed": 2_147_483_648,
            },
            "seed",
        ),
        (
            {
                "app_id": "alibaba/happy-horse/reference-to-video",
                "prompt": "Animate character1.",
                "image_urls": ["https://example.com/character-1.png"],
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_happy_horse_reference_to_video_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        HappyHorseReferenceToVideoConfig.model_validate(payload)

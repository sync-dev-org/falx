from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Wan30PrimeImageToVideoConfig, validate_parameters

APP_ID = "alibaba/wan-3.0-prime/image-to-video"


def test_wan_3_0_prime_image_to_video_accepts_documented_defaults() -> None:
    config = Wan30PrimeImageToVideoConfig(
        app_id=APP_ID,
        start_image_url="https://example.com/start.png",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": None,
        "resolution": "1080p",
        "aspect_ratio": "adaptive",
        "duration": 5,
        "audio": True,
        "enable_prompt_expansion": True,
        "enable_thinking": False,
        "seed": None,
        "enable_safety_checker": True,
        "start_image_url": "https://example.com/start.png",
        "end_image_url": None,
    }


def test_wan_3_0_prime_image_to_video_accepts_all_fields() -> None:
    config = Wan30PrimeImageToVideoConfig(
        app_id=APP_ID,
        prompt="The subject slowly turns toward the camera.",
        resolution="720p",
        aspect_ratio="4:3",
        duration=None,
        audio=False,
        enable_prompt_expansion=False,
        enable_thinking=True,
        seed=0,
        enable_safety_checker=False,
        start_image_url="https://example.com/start.webp",
        end_image_url="https://example.com/end.webp",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "The subject slowly turns toward the camera.",
        "resolution": "720p",
        "aspect_ratio": "4:3",
        "duration": None,
        "audio": False,
        "enable_prompt_expansion": False,
        "enable_thinking": True,
        "seed": 0,
        "enable_safety_checker": False,
        "start_image_url": "https://example.com/start.webp",
        "end_image_url": "https://example.com/end.webp",
    }


def test_wan_3_0_prime_image_to_video_routes_through_registered_validator() -> None:
    validated = validate_parameters(
        APP_ID,
        {"start_image_url": "https://example.com/start.png"},
    )

    assert isinstance(validated, Wan30PrimeImageToVideoConfig)


@pytest.mark.parametrize("resolution", ["480p", "720p", "1080p"])
def test_wan_3_0_prime_image_to_video_accepts_resolution_enum(resolution: str) -> None:
    config = Wan30PrimeImageToVideoConfig(
        app_id=APP_ID,
        start_image_url="https://example.com/start.png",
        resolution=resolution,
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("aspect_ratio", ["adaptive", "16:9", "4:3", "1:1", "3:4", "9:16"])
def test_wan_3_0_prime_image_to_video_accepts_aspect_ratio_enum(aspect_ratio: str) -> None:
    config = Wan30PrimeImageToVideoConfig(
        app_id=APP_ID,
        start_image_url="https://example.com/start.png",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("duration", [None, 2, 30])
def test_wan_3_0_prime_image_to_video_accepts_duration_boundaries(
    duration: int | None,
) -> None:
    config = Wan30PrimeImageToVideoConfig(
        app_id=APP_ID,
        start_image_url="https://example.com/start.png",
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize("seed", [None, 0, 2_147_483_647])
def test_wan_3_0_prime_image_to_video_accepts_seed_boundaries(seed: int | None) -> None:
    config = Wan30PrimeImageToVideoConfig(
        app_id=APP_ID,
        start_image_url="https://example.com/start.png",
        seed=seed,
    )

    assert config.seed == seed


def test_wan_3_0_prime_image_to_video_accepts_empty_and_max_length_prompts() -> None:
    empty = Wan30PrimeImageToVideoConfig(
        app_id=APP_ID,
        start_image_url="https://example.com/start.png",
        prompt="",
    )
    maximum = Wan30PrimeImageToVideoConfig(
        app_id=APP_ID,
        start_image_url="https://example.com/start.png",
        prompt="x" * 5000,
    )

    assert empty.prompt == ""
    assert maximum.prompt is not None
    assert len(maximum.prompt) == 5000


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID}, "start_image_url"),
        (
            {
                "app_id": APP_ID,
                "start_image_url": "https://example.com/start.png",
                "prompt": "x" * 5001,
            },
            "prompt",
        ),
        (
            {
                "app_id": APP_ID,
                "start_image_url": "https://example.com/start.png",
                "resolution": "4k",
            },
            "resolution",
        ),
        (
            {
                "app_id": APP_ID,
                "start_image_url": "https://example.com/start.png",
                "aspect_ratio": "21:9",
            },
            "aspect_ratio",
        ),
        (
            {"app_id": APP_ID, "start_image_url": "https://example.com/start.png", "duration": 1},
            "duration",
        ),
        (
            {"app_id": APP_ID, "start_image_url": "https://example.com/start.png", "duration": 31},
            "duration",
        ),
        (
            {"app_id": APP_ID, "start_image_url": "https://example.com/start.png", "seed": -1},
            "seed",
        ),
        (
            {
                "app_id": APP_ID,
                "start_image_url": "https://example.com/start.png",
                "seed": 2_147_483_648,
            },
            "seed",
        ),
        (
            {
                "app_id": APP_ID,
                "start_image_url": "https://example.com/start.png",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_wan_3_0_prime_image_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Wan30PrimeImageToVideoConfig.model_validate(payload)

from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Wan30PrimeTextToVideoConfig, validate_parameters

APP_ID = "alibaba/wan-3.0-prime/text-to-video"


def test_wan_3_0_prime_text_to_video_accepts_documented_defaults() -> None:
    config = Wan30PrimeTextToVideoConfig(
        app_id=APP_ID,
        prompt="A red panda walks through a bamboo forest at sunrise.",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A red panda walks through a bamboo forest at sunrise.",
        "resolution": "1080p",
        "aspect_ratio": "adaptive",
        "duration": 5,
        "audio": True,
        "enable_prompt_expansion": True,
        "enable_thinking": False,
        "seed": None,
        "enable_safety_checker": True,
    }


def test_wan_3_0_prime_text_to_video_accepts_all_fields() -> None:
    config = Wan30PrimeTextToVideoConfig(
        app_id=APP_ID,
        prompt="A cinematic city street fills with morning light.",
        resolution="480p",
        aspect_ratio="9:16",
        duration=None,
        audio=False,
        enable_prompt_expansion=False,
        enable_thinking=True,
        seed=2_147_483_647,
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A cinematic city street fills with morning light.",
        "resolution": "480p",
        "aspect_ratio": "9:16",
        "duration": None,
        "audio": False,
        "enable_prompt_expansion": False,
        "enable_thinking": True,
        "seed": 2_147_483_647,
        "enable_safety_checker": False,
    }


def test_wan_3_0_prime_text_to_video_routes_through_registered_validator() -> None:
    validated = validate_parameters(APP_ID, {"prompt": "A paper lantern rises into the night."})

    assert isinstance(validated, Wan30PrimeTextToVideoConfig)


@pytest.mark.parametrize("resolution", ["480p", "720p", "1080p"])
def test_wan_3_0_prime_text_to_video_accepts_resolution_enum(resolution: str) -> None:
    config = Wan30PrimeTextToVideoConfig(
        app_id=APP_ID,
        prompt="A dancer crosses a rain-soaked stage.",
        resolution=resolution,
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("aspect_ratio", ["adaptive", "16:9", "4:3", "1:1", "3:4", "9:16"])
def test_wan_3_0_prime_text_to_video_accepts_aspect_ratio_enum(aspect_ratio: str) -> None:
    config = Wan30PrimeTextToVideoConfig(
        app_id=APP_ID,
        prompt="A dancer crosses a rain-soaked stage.",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("duration", [None, 2, 30])
def test_wan_3_0_prime_text_to_video_accepts_duration_boundaries(
    duration: int | None,
) -> None:
    config = Wan30PrimeTextToVideoConfig(
        app_id=APP_ID,
        prompt="A train passes through a snowy valley.",
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize("seed", [None, 0, 2_147_483_647])
def test_wan_3_0_prime_text_to_video_accepts_seed_boundaries(seed: int | None) -> None:
    config = Wan30PrimeTextToVideoConfig(
        app_id=APP_ID,
        prompt="A train passes through a snowy valley.",
        seed=seed,
    )

    assert config.seed == seed


def test_wan_3_0_prime_text_to_video_accepts_prompt_length_boundaries() -> None:
    assert Wan30PrimeTextToVideoConfig(app_id=APP_ID, prompt="x").prompt == "x"
    assert len(Wan30PrimeTextToVideoConfig(app_id=APP_ID, prompt="x" * 5000).prompt) == 5000


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID}, "prompt"),
        ({"app_id": APP_ID, "prompt": ""}, "prompt"),
        ({"app_id": APP_ID, "prompt": "x" * 5001}, "prompt"),
        ({"app_id": APP_ID, "prompt": "A lighthouse in fog.", "resolution": "4k"}, "resolution"),
        (
            {"app_id": APP_ID, "prompt": "A lighthouse in fog.", "aspect_ratio": "21:9"},
            "aspect_ratio",
        ),
        ({"app_id": APP_ID, "prompt": "A lighthouse in fog.", "duration": 1}, "duration"),
        ({"app_id": APP_ID, "prompt": "A lighthouse in fog.", "duration": 31}, "duration"),
        ({"app_id": APP_ID, "prompt": "A lighthouse in fog.", "seed": -1}, "seed"),
        (
            {"app_id": APP_ID, "prompt": "A lighthouse in fog.", "seed": 2_147_483_648},
            "seed",
        ),
        ({"app_id": APP_ID, "prompt": "A lighthouse in fog.", "unexpected": True}, "unexpected"),
    ],
)
def test_wan_3_0_prime_text_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Wan30PrimeTextToVideoConfig.model_validate(payload)

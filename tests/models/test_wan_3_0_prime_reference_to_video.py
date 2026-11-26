from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Wan30PrimeReferenceToVideoConfig, validate_parameters

APP_ID = "alibaba/wan-3.0-prime/reference-to-video"


def test_wan_3_0_prime_reference_to_video_accepts_no_parameter_fields() -> None:
    config = Wan30PrimeReferenceToVideoConfig(app_id=APP_ID)

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
        "reference_image_urls": [],
        "reference_video_urls": [],
        "reference_audio_urls": [],
        "file_url": None,
        "web_url": None,
    }


def test_wan_3_0_prime_reference_to_video_declares_no_required_parameters() -> None:
    schema = Wan30PrimeReferenceToVideoConfig.model_json_schema()

    assert schema["required"] == ["app_id"]


@pytest.mark.parametrize(
    ("field_name", "max_items"),
    [
        ("reference_image_urls", 10),
        ("reference_video_urls", 5),
        ("reference_audio_urls", 5),
    ],
)
def test_wan_3_0_prime_reference_to_video_declares_array_only_reference_fields(
    field_name: str,
    max_items: int,
) -> None:
    property_schema = Wan30PrimeReferenceToVideoConfig.model_json_schema()["properties"][
        field_name
    ]

    assert property_schema["type"] == "array"
    assert property_schema["maxItems"] == max_items
    assert "anyOf" not in property_schema
    assert "default" not in property_schema


def test_wan_3_0_prime_reference_to_video_routes_empty_parameters() -> None:
    validated = validate_parameters(APP_ID, {})

    assert isinstance(validated, Wan30PrimeReferenceToVideoConfig)


def test_wan_3_0_prime_reference_to_video_accepts_all_fields_at_boundaries() -> None:
    config = Wan30PrimeReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use Image 1 as the subject and Video 1 as the motion reference.",
        resolution="480p",
        aspect_ratio="3:4",
        duration=30,
        audio=False,
        enable_prompt_expansion=False,
        enable_thinking=True,
        seed=2_147_483_647,
        enable_safety_checker=False,
        reference_image_urls=[f"https://example.com/image-{index}.png" for index in range(10)],
        reference_video_urls=[f"https://example.com/video-{index}.mp4" for index in range(5)],
        reference_audio_urls=[f"https://example.com/audio-{index}.mp3" for index in range(5)],
        file_url="https://example.com/brief.pdf",
        web_url="https://example.com/campaign",
    )

    assert len(config.reference_image_urls) == 10
    assert len(config.reference_video_urls) == 5
    assert len(config.reference_audio_urls) == 5
    assert config.file_url == "https://example.com/brief.pdf"
    assert config.web_url == "https://example.com/campaign"


def test_wan_3_0_prime_reference_to_video_accepts_explicit_null_nullable_fields() -> None:
    config = Wan30PrimeReferenceToVideoConfig(
        app_id=APP_ID,
        prompt=None,
        duration=None,
        seed=None,
        file_url=None,
        web_url=None,
    )

    assert config.prompt is None
    assert config.duration is None


@pytest.mark.parametrize(
    "field_name",
    ["reference_image_urls", "reference_video_urls", "reference_audio_urls"],
)
def test_wan_3_0_prime_reference_to_video_rejects_explicit_null_reference_fields(
    field_name: str,
) -> None:
    with pytest.raises(ValidationError, match=field_name):
        Wan30PrimeReferenceToVideoConfig.model_validate(
            {"app_id": APP_ID, field_name: None}
        )


def test_wan_3_0_prime_reference_to_video_accepts_empty_prompt_and_reference_lists() -> None:
    config = Wan30PrimeReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="",
        reference_image_urls=[],
        reference_video_urls=[],
        reference_audio_urls=[],
    )

    assert config.prompt == ""
    assert config.reference_image_urls == []
    assert config.reference_video_urls == []
    assert config.reference_audio_urls == []


def test_wan_3_0_prime_reference_to_video_accepts_max_length_prompt() -> None:
    config = Wan30PrimeReferenceToVideoConfig(app_id=APP_ID, prompt="x" * 20000)

    assert config.prompt == "x" * 20000


@pytest.mark.parametrize("resolution", ["480p", "720p", "1080p"])
def test_wan_3_0_prime_reference_to_video_accepts_resolution_enum(resolution: str) -> None:
    config = Wan30PrimeReferenceToVideoConfig(app_id=APP_ID, resolution=resolution)

    assert config.resolution == resolution


@pytest.mark.parametrize("aspect_ratio", ["adaptive", "16:9", "4:3", "1:1", "3:4", "9:16"])
def test_wan_3_0_prime_reference_to_video_accepts_aspect_ratio_enum(aspect_ratio: str) -> None:
    config = Wan30PrimeReferenceToVideoConfig(app_id=APP_ID, aspect_ratio=aspect_ratio)

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("duration", [None, 2, 30])
def test_wan_3_0_prime_reference_to_video_accepts_duration_boundaries(
    duration: int | None,
) -> None:
    config = Wan30PrimeReferenceToVideoConfig(app_id=APP_ID, duration=duration)

    assert config.duration == duration


@pytest.mark.parametrize("seed", [None, 0, 2_147_483_647])
def test_wan_3_0_prime_reference_to_video_accepts_seed_boundaries(seed: int | None) -> None:
    config = Wan30PrimeReferenceToVideoConfig(app_id=APP_ID, seed=seed)

    assert config.seed == seed


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID, "prompt": "x" * 20001}, "prompt"),
        ({"app_id": APP_ID, "resolution": "4k"}, "resolution"),
        ({"app_id": APP_ID, "aspect_ratio": "21:9"}, "aspect_ratio"),
        ({"app_id": APP_ID, "duration": 1}, "duration"),
        ({"app_id": APP_ID, "duration": 31}, "duration"),
        ({"app_id": APP_ID, "seed": -1}, "seed"),
        ({"app_id": APP_ID, "seed": 2_147_483_648}, "seed"),
        (
            {
                "app_id": APP_ID,
                "reference_image_urls": [
                    f"https://example.com/image-{index}.png" for index in range(11)
                ],
            },
            "reference_image_urls",
        ),
        (
            {
                "app_id": APP_ID,
                "reference_video_urls": [
                    f"https://example.com/video-{index}.mp4" for index in range(6)
                ],
            },
            "reference_video_urls",
        ),
        (
            {
                "app_id": APP_ID,
                "reference_audio_urls": [
                    f"https://example.com/audio-{index}.mp3" for index in range(6)
                ],
            },
            "reference_audio_urls",
        ),
        ({"app_id": APP_ID, "unexpected": True}, "unexpected"),
    ],
)
def test_wan_3_0_prime_reference_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Wan30PrimeReferenceToVideoConfig.model_validate(payload)

from __future__ import annotations

from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    GeminiOmniFlashV11EditConfig,
    GeminiOmniFlashV11ImageToVideoConfig,
    GeminiOmniFlashV11ReferenceToVideoConfig,
    GeminiOmniFlashV11TextToVideoConfig,
    config_class_for_app_id,
)

_VIDEO_CONFIG_CASES: tuple[tuple[type[Any], dict[str, Any]], ...] = (
    (
        GeminiOmniFlashV11TextToVideoConfig,
        {"app_id": "google/gemini-omni-flash/v1.1/text-to-video"},
    ),
    (
        GeminiOmniFlashV11ImageToVideoConfig,
        {
            "app_id": "google/gemini-omni-flash/v1.1/image-to-video",
            "image_url": "https://example.com/start.png",
        },
    ),
    (
        GeminiOmniFlashV11ReferenceToVideoConfig,
        {"app_id": "google/gemini-omni-flash/v1.1/reference-to-video"},
    ),
)


def test_gemini_omni_flash_v1_1_edit_accepts_only_its_api_fields() -> None:
    config = GeminiOmniFlashV11EditConfig(
        app_id="google/gemini-omni-flash/v1.1/edit",
        prompt="Make this video look hand-painted.",
        video_url="https://example.com/input.mp4",
    )

    assert config.model_dump() == {
        "app_id": "google/gemini-omni-flash/v1.1/edit",
        "prompt": "Make this video look hand-painted.",
        "video_url": "https://example.com/input.mp4",
        "resolution": "720p",
    }

    for extra_field in ("duration", "aspect_ratio"):
        with pytest.raises(ValidationError, match=extra_field):
            GeminiOmniFlashV11EditConfig.model_validate(
                {
                    "app_id": "google/gemini-omni-flash/v1.1/edit",
                    "prompt": "Make this video look hand-painted.",
                    "video_url": "https://example.com/input.mp4",
                    extra_field: 8 if extra_field == "duration" else "16:9",
                }
            )


def test_gemini_omni_flash_v1_1_text_to_video_matches_api_defaults() -> None:
    config = GeminiOmniFlashV11TextToVideoConfig(
        app_id="google/gemini-omni-flash/v1.1/text-to-video",
        prompt="A lighthouse beam sweeps across a dark sea.",
    )

    assert config.model_dump() == {
        "app_id": "google/gemini-omni-flash/v1.1/text-to-video",
        "prompt": "A lighthouse beam sweeps across a dark sea.",
        "aspect_ratio": "16:9",
        "resolution": "720p",
        "duration": 8,
    }


def test_gemini_omni_flash_v1_1_image_to_video_matches_api_defaults() -> None:
    config = GeminiOmniFlashV11ImageToVideoConfig(
        app_id="google/gemini-omni-flash/v1.1/image-to-video",
        prompt="The dog turns its head in warm sunlight.",
        image_url="https://example.com/start.png",
    )

    assert config.model_dump() == {
        "app_id": "google/gemini-omni-flash/v1.1/image-to-video",
        "prompt": "The dog turns its head in warm sunlight.",
        "image_url": "https://example.com/start.png",
        "end_image_url": None,
        "aspect_ratio": "16:9",
        "resolution": "720p",
        "duration": 8,
    }


def test_gemini_omni_flash_v1_1_reference_to_video_matches_api_defaults() -> None:
    config = GeminiOmniFlashV11ReferenceToVideoConfig(
        app_id="google/gemini-omni-flash/v1.1/reference-to-video",
        prompt="Use the subject from <IMAGE_REF_0> in the setting from <VIDEO_REF_0>.",
    )

    assert config.model_dump() == {
        "app_id": "google/gemini-omni-flash/v1.1/reference-to-video",
        "prompt": "Use the subject from <IMAGE_REF_0> in the setting from <VIDEO_REF_0>.",
        "image_urls": None,
        "reference_video_urls": None,
        "aspect_ratio": "16:9",
        "resolution": "720p",
        "duration": 8,
    }


@pytest.mark.parametrize("resolution", ["360p", "720p", "1080p", "4k"])
def test_gemini_omni_flash_v1_1_accepts_api_resolutions(resolution: str) -> None:
    config = GeminiOmniFlashV11TextToVideoConfig(
        app_id="google/gemini-omni-flash/v1.1/text-to-video",
        prompt="A cinematic city at dawn.",
        resolution=resolution,
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("aspect_ratio", ["16:9", "9:16"])
def test_gemini_omni_flash_v1_1_accepts_api_aspect_ratios(aspect_ratio: str) -> None:
    config = GeminiOmniFlashV11TextToVideoConfig(
        app_id="google/gemini-omni-flash/v1.1/text-to-video",
        prompt="A cinematic city at dawn.",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize(
    ("config_class", "payload"),
    _VIDEO_CONFIG_CASES,
    ids=("text-to-video", "image-to-video", "reference-to-video"),
)
@pytest.mark.parametrize("duration", (3, 10))
def test_gemini_omni_flash_v1_1_video_configs_accept_api_duration_boundaries(
    config_class: type[Any],
    payload: dict[str, Any],
    duration: int,
) -> None:
    config = config_class.model_validate(
        {
            **payload,
            "prompt": "A cinematic city at dawn.",
            "duration": duration,
        }
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("resolution", "480p"),
        ("aspect_ratio", "1:1"),
    ],
)
def test_gemini_omni_flash_v1_1_rejects_literal_values_outside_api_schema(
    field: str,
    value: str | int,
) -> None:
    payload: dict[str, Any] = {
        "app_id": "google/gemini-omni-flash/v1.1/text-to-video",
        "prompt": "A cinematic city at dawn.",
        field: value,
    }

    with pytest.raises(ValidationError, match=field):
        GeminiOmniFlashV11TextToVideoConfig.model_validate(payload)


@pytest.mark.parametrize(
    ("config_class", "payload"),
    _VIDEO_CONFIG_CASES,
    ids=("text-to-video", "image-to-video", "reference-to-video"),
)
@pytest.mark.parametrize("duration", (2, 11))
def test_gemini_omni_flash_v1_1_video_configs_reject_duration_outside_api_range(
    config_class: type[Any],
    payload: dict[str, Any],
    duration: int,
) -> None:
    with pytest.raises(ValidationError, match="duration"):
        config_class.model_validate(
            {
                **payload,
                "prompt": "A cinematic city at dawn.",
                "duration": duration,
            }
        )


@pytest.mark.parametrize(
    ("config_class", "payload"),
    [
        (
            GeminiOmniFlashV11EditConfig,
            {
                "app_id": "google/gemini-omni-flash/v1.1/edit",
                "video_url": "https://example.com/input.mp4",
            },
        ),
        (
            GeminiOmniFlashV11TextToVideoConfig,
            {"app_id": "google/gemini-omni-flash/v1.1/text-to-video"},
        ),
        (
            GeminiOmniFlashV11ImageToVideoConfig,
            {
                "app_id": "google/gemini-omni-flash/v1.1/image-to-video",
                "image_url": "https://example.com/start.png",
            },
        ),
        (
            GeminiOmniFlashV11ReferenceToVideoConfig,
            {"app_id": "google/gemini-omni-flash/v1.1/reference-to-video"},
        ),
    ],
)
def test_gemini_omni_flash_v1_1_requires_prompt(
    config_class: type[Any],
    payload: dict[str, Any],
) -> None:
    with pytest.raises(ValidationError, match="prompt"):
        config_class.model_validate(payload)


def test_gemini_omni_flash_v1_1_requires_route_specific_media() -> None:
    with pytest.raises(ValidationError, match="video_url"):
        GeminiOmniFlashV11EditConfig(
            app_id="google/gemini-omni-flash/v1.1/edit",
            prompt="Make this video look hand-painted.",
        )

    with pytest.raises(ValidationError, match="image_url"):
        GeminiOmniFlashV11ImageToVideoConfig(
            app_id="google/gemini-omni-flash/v1.1/image-to-video",
            prompt="Animate the subject.",
        )


@pytest.mark.parametrize(
    ("config_class", "payload"),
    [
        (
            GeminiOmniFlashV11EditConfig,
            {
                "app_id": "google/gemini-omni-flash/v1.1/edit",
                "video_url": "https://example.com/input.mp4",
            },
        ),
        (
            GeminiOmniFlashV11TextToVideoConfig,
            {"app_id": "google/gemini-omni-flash/v1.1/text-to-video"},
        ),
        (
            GeminiOmniFlashV11ImageToVideoConfig,
            {
                "app_id": "google/gemini-omni-flash/v1.1/image-to-video",
                "image_url": "https://example.com/start.png",
            },
        ),
        (
            GeminiOmniFlashV11ReferenceToVideoConfig,
            {"app_id": "google/gemini-omni-flash/v1.1/reference-to-video"},
        ),
    ],
)
def test_gemini_omni_flash_v1_1_limits_prompt_to_20000_characters(
    config_class: type[Any],
    payload: dict[str, Any],
) -> None:
    config_class.model_validate({**payload, "prompt": "x" * 20_000})

    with pytest.raises(ValidationError, match="prompt"):
        config_class.model_validate({**payload, "prompt": "x" * 20_001})


def test_gemini_omni_flash_v1_1_reference_media_limits_match_api_schema() -> None:
    config = GeminiOmniFlashV11ReferenceToVideoConfig(
        app_id="google/gemini-omni-flash/v1.1/reference-to-video",
        prompt="Combine all references.",
        image_urls=[f"https://example.com/image-{index}.png" for index in range(10)],
        reference_video_urls=[f"https://example.com/video-{index}.mp4" for index in range(3)],
    )

    assert len(config.image_urls or []) == 10
    assert len(config.reference_video_urls or []) == 3

    with pytest.raises(ValidationError, match="image_urls"):
        GeminiOmniFlashV11ReferenceToVideoConfig(
            app_id="google/gemini-omni-flash/v1.1/reference-to-video",
            prompt="Combine all references.",
            image_urls=[f"https://example.com/image-{index}.png" for index in range(11)],
        )

    with pytest.raises(ValidationError, match="reference_video_urls"):
        GeminiOmniFlashV11ReferenceToVideoConfig(
            app_id="google/gemini-omni-flash/v1.1/reference-to-video",
            prompt="Combine all references.",
            reference_video_urls=[f"https://example.com/video-{index}.mp4" for index in range(4)],
        )

    schema = GeminiOmniFlashV11ReferenceToVideoConfig.model_json_schema()
    assert schema["properties"]["image_urls"]["anyOf"][0]["maxItems"] == 10
    video_schema = schema["properties"]["reference_video_urls"]
    assert video_schema["anyOf"][0]["maxItems"] == 3
    assert "ten seconds" in video_schema["description"]


def test_gemini_omni_flash_v1_1_models_are_registered_and_discriminated() -> None:
    expected_classes = {
        "google/gemini-omni-flash/v1.1/edit": GeminiOmniFlashV11EditConfig,
        "google/gemini-omni-flash/v1.1/text-to-video": GeminiOmniFlashV11TextToVideoConfig,
        "google/gemini-omni-flash/v1.1/image-to-video": GeminiOmniFlashV11ImageToVideoConfig,
        "google/gemini-omni-flash/v1.1/reference-to-video": (
            GeminiOmniFlashV11ReferenceToVideoConfig
        ),
    }
    adapter: TypeAdapter[Any] = TypeAdapter(FalConfig)

    assert expected_classes.keys() <= SUPPORTED_APP_IDS
    for app_id, expected_class in expected_classes.items():
        assert config_class_for_app_id(app_id) is expected_class
        payload: dict[str, Any] = {"app_id": app_id, "prompt": "A cinematic scene."}
        if app_id.endswith("/edit"):
            payload["video_url"] = "https://example.com/input.mp4"
        elif app_id.endswith("/image-to-video"):
            payload["image_url"] = "https://example.com/start.png"
        assert isinstance(adapter.validate_python(payload), expected_class)

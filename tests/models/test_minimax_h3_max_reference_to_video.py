from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    MinimaxH3MaxReferenceToVideoConfig,
    validate_parameters,
)

APP_ID = "minimax/h3-max/reference-to-video"


def test_minimax_h3_max_reference_to_video_accepts_schema_defaults() -> None:
    config = MinimaxH3MaxReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Keep the woman and dog consistent while they walk through a garden.",
        prompt_expansion_mode="balanced",
    )

    assert config.model_dump() == {
        "target_audio_url": None,
        "image_url": None,
        "end_image_url": None,
        "middle_image_url": None,
        "middle_frame_time": None,
        "reference_conditions": [],
        "app_id": APP_ID,
        "prompt": "Keep the woman and dog consistent while they walk through a garden.",
        "duration": 5,
        "resolution": "768P",
        "seed": None,
        "enable_safety_checker": True,
        "sync_mode": False,
        "prompt_expansion_mode": "balanced",
        "aspect_ratio": "adaptive",
        "reference_image_urls": [],
        "reference_video_urls": [],
        "reference_audio_urls": [],
    }


def test_minimax_h3_max_reference_to_video_accepts_all_fields() -> None:
    config = MinimaxH3MaxReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use Image 1, Video 1, and Audio 1 to guide the scene.",
        duration=15,
        resolution="1080P",
        seed=42,
        enable_safety_checker=False,
        sync_mode=True,
        prompt_expansion_mode="quality",
        aspect_ratio="21:9",
        reference_image_urls=["https://example.com/subject.png"],
        reference_video_urls=["https://example.com/motion.mp4"],
        reference_audio_urls=["https://example.com/dialogue.wav"],
    )

    assert config.model_dump() == {
        "target_audio_url": None,
        "image_url": None,
        "end_image_url": None,
        "middle_image_url": None,
        "middle_frame_time": None,
        "reference_conditions": [],
        "app_id": APP_ID,
        "prompt": "Use Image 1, Video 1, and Audio 1 to guide the scene.",
        "duration": 15,
        "resolution": "1080P",
        "seed": 42,
        "enable_safety_checker": False,
        "sync_mode": True,
        "prompt_expansion_mode": "quality",
        "aspect_ratio": "21:9",
        "reference_image_urls": ["https://example.com/subject.png"],
        "reference_video_urls": ["https://example.com/motion.mp4"],
        "reference_audio_urls": ["https://example.com/dialogue.wav"],
    }


def test_minimax_h3_max_reference_to_video_preserves_required_default_in_schema() -> None:
    schema = MinimaxH3MaxReferenceToVideoConfig.model_json_schema()

    assert set(schema["required"]) == {"app_id", "prompt", "prompt_expansion_mode"}
    assert schema["properties"]["prompt_expansion_mode"]["default"] == "balanced"


@pytest.mark.parametrize(
    ("field_name", "max_items"),
    [
        ("reference_image_urls", 9),
        ("reference_video_urls", 3),
        ("reference_audio_urls", 3),
    ],
)
def test_minimax_h3_max_reference_to_video_declares_optional_array_only_reference_fields(
    field_name: str,
    max_items: int,
) -> None:
    schema = MinimaxH3MaxReferenceToVideoConfig.model_json_schema()
    property_schema = schema["properties"][field_name]

    assert field_name not in schema["required"]
    assert property_schema["type"] == "array"
    assert property_schema["maxItems"] == max_items
    assert "anyOf" not in property_schema
    assert "default" not in property_schema


@pytest.mark.parametrize("resolution", ["480P", "768P", "1080P"])
def test_minimax_h3_max_reference_to_video_accepts_resolution_enum(resolution: str) -> None:
    config = MinimaxH3MaxReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use Image 1 as the visual reference.",
        prompt_expansion_mode="balanced",
        resolution=resolution,
    )

    assert config.resolution == resolution


@pytest.mark.parametrize(
    "aspect_ratio",
    ["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"],
)
def test_minimax_h3_max_reference_to_video_accepts_aspect_ratio_enum(
    aspect_ratio: str,
) -> None:
    config = MinimaxH3MaxReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use Image 1 as the visual reference.",
        prompt_expansion_mode="balanced",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("duration", [0.92, 1.5, 15])
def test_minimax_h3_max_reference_to_video_accepts_duration_boundaries(
    duration: float,
) -> None:
    config = MinimaxH3MaxReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use Image 1 as the visual reference.",
        prompt_expansion_mode="balanced",
        duration=duration,
    )

    assert config.duration == duration


def test_minimax_h3_max_reference_to_video_does_not_invent_prompt_expansion_enum() -> None:
    config = MinimaxH3MaxReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use Image 1 as the visual reference.",
        prompt_expansion_mode="provider-defined-mode",
    )

    assert config.prompt_expansion_mode == "provider-defined-mode"


@pytest.mark.parametrize(
    "field_name",
    ["reference_image_urls", "reference_video_urls", "reference_audio_urls"],
)
def test_minimax_h3_max_reference_to_video_rejects_explicit_null_reference_fields(
    field_name: str,
) -> None:
    with pytest.raises(ValidationError, match=field_name):
        MinimaxH3MaxReferenceToVideoConfig.model_validate(
            {
                "app_id": APP_ID,
                "prompt": "Use Image 1 as the visual reference.",
                "prompt_expansion_mode": "balanced",
                field_name: None,
            }
        )


@pytest.mark.parametrize(
    ("field_name", "count"),
    [
        ("reference_image_urls", 10),
        ("reference_video_urls", 4),
        ("reference_audio_urls", 4),
    ],
)
def test_minimax_h3_max_reference_to_video_rejects_too_many_files_per_modality(
    field_name: str,
    count: int,
) -> None:
    payload: dict[str, object] = {
        "app_id": APP_ID,
        "prompt": "Use Image 1 as the visual reference.",
        "prompt_expansion_mode": "balanced",
        "reference_image_urls": ["https://example.com/visual.png"],
        field_name: [f"https://example.com/reference-{index}" for index in range(count)],
    }

    with pytest.raises(ValidationError, match=field_name):
        MinimaxH3MaxReferenceToVideoConfig.model_validate(payload)


def test_minimax_h3_max_reference_to_video_accepts_full_twelve_file_budget() -> None:
    config = MinimaxH3MaxReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use the full multimodal reference budget.",
        prompt_expansion_mode="balanced",
        reference_image_urls=[f"https://example.com/image-{index}.png" for index in range(9)],
        reference_video_urls=[f"https://example.com/video-{index}.mp4" for index in range(3)],
    )

    assert len(config.reference_image_urls) + len(config.reference_video_urls) == 12


def test_minimax_h3_max_reference_to_video_rejects_more_than_twelve_files() -> None:
    with pytest.raises(ValidationError, match="must be <= 12"):
        MinimaxH3MaxReferenceToVideoConfig(
            app_id=APP_ID,
            prompt="Use the supplied references.",
            prompt_expansion_mode="balanced",
            reference_image_urls=[
                f"https://example.com/image-{index}.png" for index in range(9)
            ],
            reference_video_urls=[
                f"https://example.com/video-{index}.mp4" for index in range(3)
            ],
            reference_audio_urls=["https://example.com/audio.wav"],
        )


def test_minimax_h3_max_reference_to_video_accepts_audio_without_visual_reference() -> None:
    config = MinimaxH3MaxReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use Audio 1 to guide the scene.",
        prompt_expansion_mode="balanced",
        reference_audio_urls=["https://example.com/dialogue.wav"],
    )

    assert config.model_dump()["reference_audio_urls"] == ["https://example.com/dialogue.wav"]


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID, "prompt_expansion_mode": "balanced"}, "prompt"),
        (
            {"app_id": APP_ID, "prompt": "Use Image 1 as the reference."},
            "prompt_expansion_mode",
        ),
        (
            {"app_id": APP_ID, "prompt": "", "prompt_expansion_mode": "balanced"},
            "prompt",
        ),
        (
            {"app_id": APP_ID, "prompt": "x" * 50_001, "prompt_expansion_mode": "balanced"},
            "prompt",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Use Image 1 as the reference.",
                "prompt_expansion_mode": "balanced",
                "resolution": "4K",
            },
            "resolution",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Use Image 1 as the reference.",
                "prompt_expansion_mode": "balanced",
                "aspect_ratio": "2:1",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Use Image 1 as the reference.",
                "prompt_expansion_mode": "balanced",
                "duration": 0.91,
            },
            "duration",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Use Image 1 as the reference.",
                "prompt_expansion_mode": "balanced",
                "duration": 16,
            },
            "duration",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Use Image 1 as the reference.",
                "prompt_expansion_mode": "balanced",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_minimax_h3_max_reference_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        MinimaxH3MaxReferenceToVideoConfig.model_validate(payload)


def test_minimax_h3_max_reference_to_video_routes_through_registry() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)
    payload = {
        "app_id": APP_ID,
        "prompt": "Use Image 1 as the visual reference.",
        "prompt_expansion_mode": "balanced",
    }

    parsed = adapter.validate_python(payload)
    validated = validate_parameters(
        APP_ID,
        {key: value for key, value in payload.items() if key != "app_id"},
    )

    assert APP_ID in SUPPORTED_APP_IDS
    assert isinstance(parsed, MinimaxH3MaxReferenceToVideoConfig)
    assert isinstance(validated, MinimaxH3MaxReferenceToVideoConfig)
    assert MinimaxH3MaxReferenceToVideoConfig.random_seed_field == "seed"

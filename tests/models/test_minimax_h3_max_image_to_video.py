from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    MinimaxH3MaxImageToVideoConfig,
    validate_parameters,
)

APP_ID = "minimax/h3-max/image-to-video"


def test_minimax_h3_max_image_to_video_accepts_schema_defaults_without_image() -> None:
    config = MinimaxH3MaxImageToVideoConfig(
        app_id=APP_ID,
        prompt="The camera slowly reveals a mountain landscape.",
        prompt_expansion_mode="balanced",
    )

    assert config.model_dump() == {
        "target_audio_url": None,
        "app_id": APP_ID,
        "image_url": None,
        "prompt_expansion_mode": "balanced",
        "resolution": "768P",
        "duration": 5,
        "seed": None,
        "prompt": "The camera slowly reveals a mountain landscape.",
        "sync_mode": False,
        "end_image_url": None,
        "enable_safety_checker": True,
    }


def test_minimax_h3_max_image_to_video_accepts_all_fields() -> None:
    config = MinimaxH3MaxImageToVideoConfig(
        app_id=APP_ID,
        image_url="https://example.com/first.png",
        prompt_expansion_mode="quality",
        resolution="480P",
        duration=15,
        seed=42,
        prompt="Clouds drift overhead while the camera pulls back.",
        sync_mode=True,
        end_image_url="https://example.com/last.png",
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "target_audio_url": None,
        "app_id": APP_ID,
        "image_url": "https://example.com/first.png",
        "prompt_expansion_mode": "quality",
        "resolution": "480P",
        "duration": 15,
        "seed": 42,
        "prompt": "Clouds drift overhead while the camera pulls back.",
        "sync_mode": True,
        "end_image_url": "https://example.com/last.png",
        "enable_safety_checker": False,
    }


def test_minimax_h3_max_image_to_video_preserves_required_default_in_json_schema() -> None:
    schema = MinimaxH3MaxImageToVideoConfig.model_json_schema()

    assert set(schema["required"]) == {"app_id", "prompt", "prompt_expansion_mode"}
    assert schema["properties"]["prompt_expansion_mode"]["default"] == "balanced"


@pytest.mark.parametrize("resolution", ["480P", "768P", "1080P"])
def test_minimax_h3_max_image_to_video_accepts_resolution_enum(resolution: str) -> None:
    config = MinimaxH3MaxImageToVideoConfig(
        app_id=APP_ID,
        prompt="Clouds drift over a quiet valley.",
        prompt_expansion_mode="balanced",
        resolution=resolution,
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("duration", [0.92, 1.5, 15])
def test_minimax_h3_max_image_to_video_accepts_duration_boundaries(duration: float) -> None:
    config = MinimaxH3MaxImageToVideoConfig(
        app_id=APP_ID,
        prompt="Clouds drift over a quiet valley.",
        prompt_expansion_mode="balanced",
        duration=duration,
    )

    assert config.duration == duration


def test_minimax_h3_max_image_to_video_does_not_invent_prompt_expansion_enum() -> None:
    config = MinimaxH3MaxImageToVideoConfig(
        app_id=APP_ID,
        prompt="Clouds drift over a quiet valley.",
        prompt_expansion_mode="provider-defined-mode",
    )

    assert config.prompt_expansion_mode == "provider-defined-mode"


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID, "prompt_expansion_mode": "balanced"}, "prompt"),
        ({"app_id": APP_ID, "prompt": "Clouds drift over a valley."}, "prompt_expansion_mode"),
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
                "prompt": "Clouds drift over a valley.",
                "prompt_expansion_mode": "balanced",
                "resolution": "4K",
            },
            "resolution",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Clouds drift over a valley.",
                "prompt_expansion_mode": "balanced",
                "duration": 0.91,
            },
            "duration",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Clouds drift over a valley.",
                "prompt_expansion_mode": "balanced",
                "duration": 16,
            },
            "duration",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Clouds drift over a valley.",
                "prompt_expansion_mode": "balanced",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_minimax_h3_max_image_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        MinimaxH3MaxImageToVideoConfig.model_validate(payload)


def test_minimax_h3_max_image_to_video_routes_through_registry() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)
    payload = {
        "app_id": APP_ID,
        "prompt": "Clouds drift over a quiet valley.",
        "prompt_expansion_mode": "balanced",
    }

    parsed = adapter.validate_python(payload)
    validated = validate_parameters(
        APP_ID,
        {key: value for key, value in payload.items() if key != "app_id"},
    )

    assert APP_ID in SUPPORTED_APP_IDS
    assert isinstance(parsed, MinimaxH3MaxImageToVideoConfig)
    assert isinstance(validated, MinimaxH3MaxImageToVideoConfig)
    assert MinimaxH3MaxImageToVideoConfig.random_seed_field == "seed"

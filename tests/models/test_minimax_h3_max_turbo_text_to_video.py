from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    MinimaxH3MaxTurboTextToVideoConfig,
    validate_parameters,
)

APP_ID = "minimax/h3-max-turbo/text-to-video"


def test_minimax_h3_max_turbo_text_to_video_accepts_schema_defaults() -> None:
    config = MinimaxH3MaxTurboTextToVideoConfig(
        app_id=APP_ID,
        prompt="A white kitten chases a butterfly across a sunlit garden.",
        prompt_expansion_mode="balanced",
    )

    assert config.model_dump() == {
        "target_audio_url": None,
        "app_id": APP_ID,
        "prompt": "A white kitten chases a butterfly across a sunlit garden.",
        "duration": 5,
        "resolution": "768P",
        "seed": None,
        "enable_safety_checker": True,
        "sync_mode": False,
        "prompt_expansion_mode": "balanced",
        "aspect_ratio": "16:9",
    }


def test_minimax_h3_max_turbo_text_to_video_accepts_all_fields() -> None:
    config = MinimaxH3MaxTurboTextToVideoConfig(
        app_id=APP_ID,
        prompt="A train crosses a mountain bridge at sunrise.",
        duration=15,
        resolution="1080P",
        seed=42,
        enable_safety_checker=False,
        sync_mode=True,
        prompt_expansion_mode="quality",
        aspect_ratio="9:16",
    )

    assert config.model_dump() == {
        "target_audio_url": None,
        "app_id": APP_ID,
        "prompt": "A train crosses a mountain bridge at sunrise.",
        "duration": 15,
        "resolution": "1080P",
        "seed": 42,
        "enable_safety_checker": False,
        "sync_mode": True,
        "prompt_expansion_mode": "quality",
        "aspect_ratio": "9:16",
    }


def test_minimax_h3_max_turbo_text_to_video_preserves_required_default_in_schema() -> None:
    schema = MinimaxH3MaxTurboTextToVideoConfig.model_json_schema()

    assert set(schema["required"]) == {"app_id", "prompt", "prompt_expansion_mode"}
    assert schema["properties"]["prompt_expansion_mode"]["default"] == "balanced"


@pytest.mark.parametrize("resolution", ["480P", "768P", "1080P"])
def test_minimax_h3_max_turbo_text_to_video_accepts_resolution_enum(
    resolution: str,
) -> None:
    config = MinimaxH3MaxTurboTextToVideoConfig(
        app_id=APP_ID,
        prompt="A quiet ocean at dusk.",
        prompt_expansion_mode="balanced",
        resolution=resolution,
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("aspect_ratio", ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"])
def test_minimax_h3_max_turbo_text_to_video_accepts_aspect_ratio_enum(
    aspect_ratio: str,
) -> None:
    config = MinimaxH3MaxTurboTextToVideoConfig(
        app_id=APP_ID,
        prompt="A quiet ocean at dusk.",
        prompt_expansion_mode="balanced",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("duration", [0.92, 1.5, 15])
def test_minimax_h3_max_turbo_text_to_video_accepts_duration_boundaries(
    duration: float,
) -> None:
    config = MinimaxH3MaxTurboTextToVideoConfig(
        app_id=APP_ID,
        prompt="A quiet ocean at dusk.",
        prompt_expansion_mode="balanced",
        duration=duration,
    )

    assert config.duration == duration


def test_minimax_h3_max_turbo_text_to_video_does_not_invent_prompt_expansion_enum() -> None:
    config = MinimaxH3MaxTurboTextToVideoConfig(
        app_id=APP_ID,
        prompt="A quiet ocean at dusk.",
        prompt_expansion_mode="provider-defined-mode",
    )

    assert config.prompt_expansion_mode == "provider-defined-mode"


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID, "prompt_expansion_mode": "balanced"}, "prompt"),
        ({"app_id": APP_ID, "prompt": "A quiet ocean at dusk."}, "prompt_expansion_mode"),
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
                "prompt": "A quiet ocean at dusk.",
                "prompt_expansion_mode": "balanced",
                "resolution": "4K",
            },
            "resolution",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "A quiet ocean at dusk.",
                "prompt_expansion_mode": "balanced",
                "aspect_ratio": "2:1",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "A quiet ocean at dusk.",
                "prompt_expansion_mode": "balanced",
                "duration": 0.91,
            },
            "duration",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "A quiet ocean at dusk.",
                "prompt_expansion_mode": "balanced",
                "duration": 16,
            },
            "duration",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "A quiet ocean at dusk.",
                "prompt_expansion_mode": "balanced",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_minimax_h3_max_turbo_text_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        MinimaxH3MaxTurboTextToVideoConfig.model_validate(payload)


def test_minimax_h3_max_turbo_text_to_video_routes_through_registry() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)
    payload = {
        "app_id": APP_ID,
        "prompt": "A quiet ocean at dusk.",
        "prompt_expansion_mode": "balanced",
    }

    parsed = adapter.validate_python(payload)
    validated = validate_parameters(
        APP_ID,
        {key: value for key, value in payload.items() if key != "app_id"},
    )

    assert APP_ID in SUPPORTED_APP_IDS
    assert isinstance(parsed, MinimaxH3MaxTurboTextToVideoConfig)
    assert isinstance(validated, MinimaxH3MaxTurboTextToVideoConfig)
    assert MinimaxH3MaxTurboTextToVideoConfig.random_seed_field == "seed"

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    H3MaxCameraKeyframe,
    MinimaxH3MaxCameraControlsConfig,
    validate_parameters,
)

APP_ID = "minimax/h3-max/camera-controls"
DEFAULT_PROMPT = (
    "The same elements in the reference are rigid. Preserve every element exactly. "
    "The entire scene is frozen. Only the camera moves. no scene motion only camera motion"
)


def _keyframe(time: float = 0.0) -> dict[str, float]:
    return {"time": time, "azimuth": 0.0, "elevation": 0.0, "distance": 1.0}


def test_minimax_h3_max_camera_controls_accepts_schema_defaults() -> None:
    config = MinimaxH3MaxCameraControlsConfig(
        app_id=APP_ID,
        image_url="https://example.com/first.png",
        prompt_expansion_mode="balanced",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": DEFAULT_PROMPT,
        "duration": 5,
        "resolution": "480P",
        "seed": None,
        "enable_safety_checker": True,
        "sync_mode": False,
        "prompt_expansion_mode": "balanced",
        "image_url": "https://example.com/first.png",
        "camera_trajectory": None,
    }


def test_minimax_h3_max_camera_controls_accepts_all_fields() -> None:
    config = MinimaxH3MaxCameraControlsConfig(
        app_id=APP_ID,
        prompt="Orbit around the subject.",
        duration=15,
        resolution="1080P",
        seed=42,
        enable_safety_checker=False,
        sync_mode=True,
        prompt_expansion_mode="quality",
        image_url="https://example.com/first.png",
        camera_trajectory=[
            {"time": 0, "azimuth": -360, "elevation": -90, "distance": 0.1},
            {"time": 1, "azimuth": 720, "elevation": 90, "distance": 2},
        ],
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Orbit around the subject.",
        "duration": 15,
        "resolution": "1080P",
        "seed": 42,
        "enable_safety_checker": False,
        "sync_mode": True,
        "prompt_expansion_mode": "quality",
        "image_url": "https://example.com/first.png",
        "camera_trajectory": [
            {"time": 0.0, "azimuth": -360.0, "elevation": -90.0, "distance": 0.1},
            {"time": 1.0, "azimuth": 720.0, "elevation": 90.0, "distance": 2.0},
        ],
    }
    assert isinstance(config.camera_trajectory[0], H3MaxCameraKeyframe)


def test_minimax_h3_max_camera_controls_preserves_required_default_in_json_schema() -> None:
    schema = MinimaxH3MaxCameraControlsConfig.model_json_schema()

    assert set(schema["required"]) == {"app_id", "image_url", "prompt_expansion_mode"}
    assert schema["properties"]["prompt_expansion_mode"]["default"] == "balanced"
    assert schema["properties"]["prompt"]["default"] == DEFAULT_PROMPT


@pytest.mark.parametrize("resolution", ["480P", "768P", "1080P"])
def test_minimax_h3_max_camera_controls_accepts_resolution_enum(resolution: str) -> None:
    config = MinimaxH3MaxCameraControlsConfig(
        app_id=APP_ID,
        image_url="https://example.com/first.png",
        prompt_expansion_mode="balanced",
        resolution=resolution,
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("duration", [5, 15])
def test_minimax_h3_max_camera_controls_accepts_duration_boundaries(duration: int) -> None:
    config = MinimaxH3MaxCameraControlsConfig(
        app_id=APP_ID,
        image_url="https://example.com/first.png",
        prompt_expansion_mode="balanced",
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize("keyframe_count", [2, 12])
def test_minimax_h3_max_camera_controls_accepts_trajectory_boundaries(
    keyframe_count: int,
) -> None:
    trajectory = [_keyframe(index / (keyframe_count - 1)) for index in range(keyframe_count)]

    config = MinimaxH3MaxCameraControlsConfig(
        app_id=APP_ID,
        image_url="https://example.com/first.png",
        prompt_expansion_mode="balanced",
        camera_trajectory=trajectory,
    )

    assert len(config.camera_trajectory) == keyframe_count


def test_minimax_h3_max_camera_controls_does_not_invent_prompt_expansion_enum() -> None:
    config = MinimaxH3MaxCameraControlsConfig(
        app_id=APP_ID,
        image_url="https://example.com/first.png",
        prompt_expansion_mode="provider-defined-mode",
    )

    assert config.prompt_expansion_mode == "provider-defined-mode"


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"prompt_expansion_mode": "balanced"}, "image_url"),
        ({"image_url": ""}, "image_url"),
        ({"image_url": "https://example.com/first.png"}, "prompt_expansion_mode"),
        (
            {
                "image_url": "https://example.com/first.png",
                "prompt_expansion_mode": "balanced",
                "prompt": "x" * 50_001,
            },
            "prompt",
        ),
        (
            {
                "image_url": "https://example.com/first.png",
                "prompt_expansion_mode": "balanced",
                "resolution": "4K",
            },
            "resolution",
        ),
        (
            {
                "image_url": "https://example.com/first.png",
                "prompt_expansion_mode": "balanced",
                "duration": 4,
            },
            "duration",
        ),
        (
            {
                "image_url": "https://example.com/first.png",
                "prompt_expansion_mode": "balanced",
                "duration": 16,
            },
            "duration",
        ),
        (
            {
                "image_url": "https://example.com/first.png",
                "prompt_expansion_mode": "balanced",
                "camera_trajectory": [_keyframe()],
            },
            "camera_trajectory",
        ),
        (
            {
                "image_url": "https://example.com/first.png",
                "prompt_expansion_mode": "balanced",
                "camera_trajectory": [_keyframe() for _ in range(13)],
            },
            "camera_trajectory",
        ),
        (
            {
                "image_url": "https://example.com/first.png",
                "prompt_expansion_mode": "balanced",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_minimax_h3_max_camera_controls_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        MinimaxH3MaxCameraControlsConfig.model_validate({"app_id": APP_ID, **parameters})


@pytest.mark.parametrize(
    ("keyframe", "needle"),
    [
        ({"time": -0.1, "azimuth": 0, "elevation": 0, "distance": 1}, "time"),
        ({"time": 1.1, "azimuth": 0, "elevation": 0, "distance": 1}, "time"),
        ({"time": 0, "azimuth": 0, "elevation": -91, "distance": 1}, "elevation"),
        ({"time": 0, "azimuth": 0, "elevation": 91, "distance": 1}, "elevation"),
        ({"time": 0, "azimuth": 0, "elevation": 0, "distance": 0}, "distance"),
        (
            {"time": 0, "azimuth": 0, "elevation": 0, "distance": 1, "unexpected": True},
            "unexpected",
        ),
    ],
)
def test_h3_max_camera_keyframe_rejects_invalid_payloads(
    keyframe: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        H3MaxCameraKeyframe.model_validate(keyframe)


def test_minimax_h3_max_camera_controls_routes_through_registry() -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)
    payload = {
        "app_id": APP_ID,
        "image_url": "https://example.com/first.png",
        "prompt_expansion_mode": "balanced",
    }

    parsed = adapter.validate_python(payload)
    validated = validate_parameters(
        APP_ID,
        {key: value for key, value in payload.items() if key != "app_id"},
    )

    assert APP_ID in SUPPORTED_APP_IDS
    assert isinstance(parsed, MinimaxH3MaxCameraControlsConfig)
    assert isinstance(validated, MinimaxH3MaxCameraControlsConfig)
    assert MinimaxH3MaxCameraControlsConfig.random_seed_field == "seed"

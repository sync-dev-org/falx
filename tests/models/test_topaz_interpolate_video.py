from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SUPPORTED_APP_IDS, TopazInterpolateVideoConfig, validate_parameters


def test_topaz_interpolate_video_config_accepts_minimal_required_fields() -> None:
    config = TopazInterpolateVideoConfig(
        app_id="topaz/interpolate/video",
        video_url="https://example.com/input.mp4",
    )

    assert config.model_dump() == {
        "app_id": "topaz/interpolate/video",
        "video_url": "https://example.com/input.mp4",
        "model": "Apollo",
        "target_fps": 60,
        "slowdown_factor": 1,
        "H264_output": False,
        "enable_safety_checker": True,
    }


def test_topaz_interpolate_video_config_accepts_all_fields() -> None:
    config = TopazInterpolateVideoConfig(
        app_id="topaz/interpolate/video",
        video_url="https://example.com/action.mp4",
        model="Aion",
        target_fps=120,
        slowdown_factor=8,
        H264_output=True,
    )

    assert config.model_dump() == {
        "app_id": "topaz/interpolate/video",
        "video_url": "https://example.com/action.mp4",
        "model": "Aion",
        "target_fps": 120,
        "slowdown_factor": 8,
        "H264_output": True,
        "enable_safety_checker": True,
    }


@pytest.mark.parametrize("model", ["Apollo", "Chronos", "Aion"])
def test_topaz_interpolate_video_config_accepts_model_enum(model: str) -> None:
    config = TopazInterpolateVideoConfig.model_validate(
        {
            "app_id": "topaz/interpolate/video",
            "video_url": "https://example.com/input.mp4",
            "model": model,
        }
    )

    assert config.model == model


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("slowdown_factor", 1),
        ("slowdown_factor", 8),
        ("target_fps", 16),
        ("target_fps", 120),
    ],
)
def test_topaz_interpolate_video_config_accepts_numeric_boundaries(
    field: str,
    value: int,
) -> None:
    config = TopazInterpolateVideoConfig.model_validate(
        {
            "app_id": "topaz/interpolate/video",
            "video_url": "https://example.com/input.mp4",
            field: value,
        }
    )

    assert getattr(config, field) == value


def test_topaz_interpolate_video_schema_matches_public_api_contract() -> None:
    schema = TopazInterpolateVideoConfig.model_json_schema()

    assert list(schema["properties"]) == [
        "app_id",
        "video_url",
        "model",
        "target_fps",
        "slowdown_factor",
        "H264_output",
        "enable_safety_checker",
    ]
    assert schema["required"] == ["app_id", "video_url"]
    assert schema["properties"]["model"]["enum"] == ["Apollo", "Chronos", "Aion"]
    assert schema["properties"]["model"]["default"] == "Apollo"
    assert schema["properties"]["target_fps"]["minimum"] == 16
    assert schema["properties"]["target_fps"]["maximum"] == 120
    assert schema["properties"]["target_fps"]["default"] == 60
    assert schema["properties"]["slowdown_factor"]["minimum"] == 1
    assert schema["properties"]["slowdown_factor"]["maximum"] == 8
    assert schema["properties"]["slowdown_factor"]["default"] == 1
    assert schema["properties"]["H264_output"]["default"] is False
    assert "output_format" not in schema["properties"]


def test_topaz_interpolate_video_is_registered_for_parameter_validation() -> None:
    assert "topaz/interpolate/video" in SUPPORTED_APP_IDS

    validated = validate_parameters(
        "topaz/interpolate/video",
        {"video_url": "https://example.com/input.mp4"},
    )

    assert isinstance(validated, TopazInterpolateVideoConfig)


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "topaz/interpolate/video"}, "video_url"),
        (
            {
                "app_id": "topaz/interpolate/video",
                "video_url": "https://example.com/input.mp4",
                "model": "apollo",
            },
            "model",
        ),
        (
            {
                "app_id": "topaz/interpolate/video",
                "video_url": "https://example.com/input.mp4",
                "slowdown_factor": 0,
            },
            "slowdown_factor",
        ),
        (
            {
                "app_id": "topaz/interpolate/video",
                "video_url": "https://example.com/input.mp4",
                "slowdown_factor": 9,
            },
            "slowdown_factor",
        ),
        (
            {
                "app_id": "topaz/interpolate/video",
                "video_url": "https://example.com/input.mp4",
                "target_fps": 15,
            },
            "target_fps",
        ),
        (
            {
                "app_id": "topaz/interpolate/video",
                "video_url": "https://example.com/input.mp4",
                "target_fps": 121,
            },
            "target_fps",
        ),
        (
            {
                "app_id": "topaz/interpolate/video",
                "video_url": "https://example.com/input.mp4",
                "output_format": "mp4",
            },
            "output_format",
        ),
    ],
)
def test_topaz_interpolate_video_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        TopazInterpolateVideoConfig.model_validate(payload)

from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    BaseFalConfig,
    config_class_for_app_id,
    validate_parameters,
)

APP_ID = "openimaginglab/flashvsr-plus"
VIDEO_URL = "https://example.com/source.mp4"


def config_for(**parameters: object) -> BaseFalConfig:
    assert APP_ID in SUPPORTED_APP_IDS
    config = validate_parameters(APP_ID, parameters)
    assert config is not None
    return config


def test_flashvsr_plus_accepts_source_video_and_schema_defaults() -> None:
    config = config_for(video_url=VIDEO_URL)

    assert config.model_dump() == {
        "app_id": APP_ID,
        "video_url": VIDEO_URL,
        "sync_mode": False,
        "video_quality": "high",
        "video_write_mode": "balanced",
        "color_fix": False,
        "seed": None,
        "enable_safety_checker": True,
        "preserve_audio": True,
        "video_output_type": "X264 (.mp4)",
        "upscale_factor": 2,
        "model": "turbo",
        "temporal_compression": 4,
    }
    assert config.random_seed_field == "seed"
    assert config_class_for_app_id(APP_ID) is type(config)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("video_quality", "low"),
        ("video_quality", "medium"),
        ("video_quality", "high"),
        ("video_quality", "maximum"),
        ("video_write_mode", "fast"),
        ("video_write_mode", "balanced"),
        ("video_write_mode", "small"),
        ("video_output_type", "X264 (.mp4)"),
        ("video_output_type", "VP9 (.webm)"),
        ("video_output_type", "PRORES4444 (.mov)"),
        ("video_output_type", "GIF (.gif)"),
        ("model", "turbo"),
        ("model", "base"),
        ("model", "v1"),
        ("temporal_compression", 1),
        ("temporal_compression", 2),
        ("temporal_compression", 4),
        ("upscale_factor", 1),
        ("upscale_factor", 1.5),
        ("upscale_factor", 4),
        ("seed", -1),
        ("seed", 123),
        ("seed", None),
        ("sync_mode", True),
        ("color_fix", True),
        ("enable_safety_checker", False),
        ("preserve_audio", False),
    ],
)
def test_flashvsr_plus_accepts_supported_options_and_bounds(field: str, value: object) -> None:
    config = config_for(video_url=VIDEO_URL, **{field: value})

    assert getattr(config, field) == value


@pytest.mark.parametrize(
    ("parameters", "field"),
    [
        ({}, "video_url"),
        ({"video_url": None}, "video_url"),
        ({"video_url": 1}, "video_url"),
        ({"upscale_factor": 0.99}, "upscale_factor"),
        ({"upscale_factor": 4.01}, "upscale_factor"),
        ({"model": "fast"}, "model"),
        ({"temporal_compression": 3}, "temporal_compression"),
        ({"video_quality": "ultra"}, "video_quality"),
        ({"video_write_mode": "slow"}, "video_write_mode"),
        ({"video_output_type": "mp4"}, "video_output_type"),
        ({"seed": 1.5}, "seed"),
        ({"color_fix": "invalid"}, "color_fix"),
        ({"unexpected": True}, "unexpected"),
    ],
)
def test_flashvsr_plus_rejects_invalid_parameters(
    parameters: dict[str, object], field: str
) -> None:
    payload = {"video_url": VIDEO_URL, **parameters} if parameters else {}
    with pytest.raises(ValidationError, match=field):
        config_for(**payload)

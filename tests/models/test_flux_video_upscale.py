from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    FluxVideoUpscaleConfig,
    config_class_for_app_id,
)


def test_flux_video_upscale_accepts_schema_defaults() -> None:
    config = FluxVideoUpscaleConfig(
        app_id="blackforestlabs/flux-video-upscale",
        video_url="https://example.com/source.mp4",
    )

    assert config.model_dump() == {
        "app_id": "blackforestlabs/flux-video-upscale",
        "video_url": "https://example.com/source.mp4",
        "upscale_factor": 2,
        "creativity": 1,
        "prompt": None,
        "safety_tolerance": 2,
    }


def test_flux_video_upscale_accepts_all_fields_and_boundaries() -> None:
    config = FluxVideoUpscaleConfig(
        app_id="blackforestlabs/flux-video-upscale",
        video_url="https://example.com/source.mp4",
        upscale_factor=3,
        creativity=0,
        prompt="Enhance the fine texture in the landscape.",
        safety_tolerance=4,
    )

    assert config.upscale_factor == 3
    assert config.creativity == 0
    assert config.prompt == "Enhance the fine texture in the landscape."
    assert config.safety_tolerance == 4


def test_flux_video_upscale_schema_preserves_source_constraints() -> None:
    schema = FluxVideoUpscaleConfig.model_json_schema()

    assert schema["properties"]["upscale_factor"]["minimum"] == 1.5
    assert schema["properties"]["upscale_factor"]["maximum"] == 3
    description = schema["properties"]["video_url"]["description"]
    assert "MP4" in description
    assert "20 seconds" in description
    assert "50 MB" in description


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({}, "video_url"),
        ({"video_url": "https://example.com/source.mp4", "upscale_factor": 1.49}, "upscale_factor"),
        ({"video_url": "https://example.com/source.mp4", "upscale_factor": 3.01}, "upscale_factor"),
        ({"video_url": "https://example.com/source.mp4", "creativity": 2}, "creativity"),
        (
            {"video_url": "https://example.com/source.mp4", "safety_tolerance": -1},
            "safety_tolerance",
        ),
        (
            {"video_url": "https://example.com/source.mp4", "safety_tolerance": 5},
            "safety_tolerance",
        ),
        ({"video_url": "https://example.com/source.mp4", "unexpected": True}, "unexpected"),
    ],
)
def test_flux_video_upscale_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        FluxVideoUpscaleConfig.model_validate(
            {"app_id": "blackforestlabs/flux-video-upscale", **payload}
        )


def test_flux_video_upscale_is_registered() -> None:
    app_id = "blackforestlabs/flux-video-upscale"

    assert app_id in SUPPORTED_APP_IDS
    assert config_class_for_app_id(app_id) is FluxVideoUpscaleConfig

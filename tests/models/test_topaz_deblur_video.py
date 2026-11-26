from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SUPPORTED_APP_IDS, TopazDeblurVideoConfig, validate_parameters


def test_topaz_deblur_video_config_accepts_minimal_required_fields() -> None:
    config = TopazDeblurVideoConfig(
        app_id="topaz/deblur/video",
        video_url="https://example.com/input.mp4",
    )

    assert config.model_dump() == {
        "app_id": "topaz/deblur/video",
        "video_url": "https://example.com/input.mp4",
        "H264_output": False,
        "enable_safety_checker": True,
    }


def test_topaz_deblur_video_config_accepts_h264_output() -> None:
    config = TopazDeblurVideoConfig(
        app_id="topaz/deblur/video",
        video_url="https://example.com/action.mp4",
        H264_output=True,
    )

    assert config.H264_output is True


def test_topaz_deblur_video_schema_matches_public_api_contract() -> None:
    schema = TopazDeblurVideoConfig.model_json_schema()

    assert list(schema["properties"]) == [
        "app_id",
        "video_url",
        "H264_output",
        "enable_safety_checker",
    ]
    assert schema["required"] == ["app_id", "video_url"]
    assert schema["properties"]["video_url"]["type"] == "string"
    assert schema["properties"]["H264_output"] == {
        "default": False,
        "description": "Whether to use H264 codec for output video. Default is H265.",
        "title": "H264 Output",
        "type": "boolean",
    }
    assert "output_format" not in schema["properties"]


def test_topaz_deblur_video_is_registered_for_parameter_validation() -> None:
    assert "topaz/deblur/video" in SUPPORTED_APP_IDS

    validated = validate_parameters(
        "topaz/deblur/video",
        {"video_url": "https://example.com/input.mp4"},
    )

    assert isinstance(validated, TopazDeblurVideoConfig)


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "topaz/deblur/video"}, "video_url"),
        (
            {
                "app_id": "topaz/upscale/video",
                "video_url": "https://example.com/input.mp4",
            },
            "app_id",
        ),
        (
            {
                "app_id": "topaz/deblur/video",
                "video_url": "https://example.com/input.mp4",
                "output_format": "mp4",
            },
            "output_format",
        ),
    ],
)
def test_topaz_deblur_video_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        TopazDeblurVideoConfig.model_validate(payload)

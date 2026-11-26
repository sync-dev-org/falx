from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

BACKGROUND_APP_IDS = (
    "bria/video/background-removal",
    "bria/video/background-removal/v3",
)
ERASE_APP_IDS = (
    "bria/video/erase/keypoints",
    "bria/video/erase/mask",
    "bria/video/erase/prompt",
)
UPSCALE_APP_ID = "bria/video/increase-resolution"
APP_IDS = (*BACKGROUND_APP_IDS, *ERASE_APP_IDS, UPSCALE_APP_ID)
VIDEO_URL = "https://example.com/source.mp4"
KEYPOINTS = ["{'x': 100, 'y': 200, 'type': 'positive'}"]
REQUIRED_INPUTS = {
    BACKGROUND_APP_IDS[0]: {"video_url": VIDEO_URL},
    BACKGROUND_APP_IDS[1]: {"video_url": VIDEO_URL},
    ERASE_APP_IDS[0]: {"video_url": VIDEO_URL, "keypoints": KEYPOINTS},
    ERASE_APP_IDS[1]: {"video_url": VIDEO_URL, "mask_video_url": "https://example.com/mask.mp4"},
    ERASE_APP_IDS[2]: {"video_url": VIDEO_URL, "prompt": "the person on the right"},
    UPSCALE_APP_ID: {"video_url": VIDEO_URL},
}
BACKGROUND_CODECS = (
    "mp4_h265",
    "mp4_h264",
    "webm_vp9",
    "mov_h265",
    "mov_proresks",
    "mkv_h265",
    "mkv_h264",
    "mkv_vp9",
    "gif",
)
ERASE_CODECS = (
    "mp4_h265",
    "mp4_h264",
    "webm_vp9",
    "gif",
    "mov_h264",
    "mov_h265",
    "mov_proresks",
    "mkv_h264",
    "mkv_h265",
    "mkv_vp9",
    "mkv_mpeg4",
)
BACKGROUND_COLORS = (
    "Transparent",
    "Black",
    "White",
    "Gray",
    "Red",
    "Green",
    "Blue",
    "Yellow",
    "Cyan",
    "Magenta",
    "Orange",
)


@pytest.mark.parametrize("app_id", APP_IDS)
def test_bria_video_endpoints_register_and_validate_defaults(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    parsed = TypeAdapter(FalConfig).validate_python({"app_id": app_id, **REQUIRED_INPUTS[app_id]})
    assert type(parsed) is config_class
    expected = {
        "app_id": app_id,
        **REQUIRED_INPUTS[app_id],
        "preserve_audio": True,
        "output_container_and_codec": "mp4_h264" if app_id in ERASE_APP_IDS else "webm_vp9",
    }
    if app_id in BACKGROUND_APP_IDS:
        expected["background_color"] = "Black"
    if app_id == BACKGROUND_APP_IDS[1]:
        expected["auto_zoom"] = False
    if app_id in ERASE_APP_IDS:
        expected["auto_trim"] = True
    if app_id == UPSCALE_APP_ID:
        expected["desired_increase"] = "2"
    assert parsed.model_dump() == expected
    assert validate_parameters(app_id, REQUIRED_INPUTS[app_id]) == parsed
    assert config_class.random_seed_field is None


@pytest.mark.parametrize(
    ("app_id", "missing"),
    [(app_id, field) for app_id in APP_IDS for field in REQUIRED_INPUTS[app_id]],
)
def test_bria_video_endpoints_reject_missing_inputs(app_id: str, missing: str) -> None:
    parameters = {**REQUIRED_INPUTS[app_id]}
    del parameters[missing]
    with pytest.raises(ValidationError) as error:
        validate_parameters(app_id, parameters)
    assert any(
        item["loc"][-1] == missing and item["type"] == "missing" for item in error.value.errors()
    )


@pytest.mark.parametrize(
    ("app_id", "codec"),
    [
        (app_id, codec)
        for app_id in APP_IDS
        for codec in (ERASE_CODECS if app_id in ERASE_APP_IDS else BACKGROUND_CODECS)
    ],
)
def test_bria_video_endpoints_accept_codec_options(app_id: str, codec: str) -> None:
    parsed = validate_parameters(
        app_id,
        {**REQUIRED_INPUTS[app_id], "preserve_audio": False, "output_container_and_codec": codec},
    )
    assert parsed is not None
    assert parsed.model_dump()["output_container_and_codec"] == codec
    assert parsed.model_dump()["preserve_audio"] is False


@pytest.mark.parametrize("app_id", BACKGROUND_APP_IDS)
@pytest.mark.parametrize("color", BACKGROUND_COLORS)
def test_bria_video_background_removal_accepts_colors(app_id: str, color: str) -> None:
    parsed = validate_parameters(app_id, {**REQUIRED_INPUTS[app_id], "background_color": color})
    assert parsed is not None
    assert parsed.model_dump()["background_color"] == color


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [
        *((app_id, "output_container_and_codec", "avi") for app_id in APP_IDS),
        *((app_id, "unknown_parameter", True) for app_id in APP_IDS),
        *((app_id, "background_color", "purple") for app_id in BACKGROUND_APP_IDS),
        (BACKGROUND_APP_IDS[0], "auto_zoom", True),
        (BACKGROUND_APP_IDS[0], "output_container_and_codec", "mov_h264"),
        (BACKGROUND_APP_IDS[1], "output_container_and_codec", "mkv_mpeg4"),
        (UPSCALE_APP_ID, "output_container_and_codec", "mov_h264"),
        (UPSCALE_APP_ID, "desired_increase", "3"),
        (UPSCALE_APP_ID, "desired_increase", 4),
        (ERASE_APP_IDS[0], "keypoints", [{"x": 100, "y": 200, "type": "positive"}]),
        (ERASE_APP_IDS[0], "keypoints", KEYPOINTS[0]),
    ],
)
def test_bria_video_endpoints_reject_invalid_parameters(
    app_id: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**REQUIRED_INPUTS[app_id], field: value})


def test_bria_video_background_removal_v3_accepts_auto_zoom() -> None:
    parsed = validate_parameters(BACKGROUND_APP_IDS[1], {"video_url": VIDEO_URL, "auto_zoom": True})
    assert parsed is not None
    assert parsed.model_dump()["auto_zoom"] is True


@pytest.mark.parametrize("app_id", ERASE_APP_IDS)
def test_bria_video_erase_can_disable_auto_trim(app_id: str) -> None:
    parsed = validate_parameters(app_id, {**REQUIRED_INPUTS[app_id], "auto_trim": False})
    assert parsed is not None
    assert parsed.model_dump()["auto_trim"] is False


def test_bria_video_increase_resolution_accepts_string_factor_four() -> None:
    parsed = validate_parameters(UPSCALE_APP_ID, {"video_url": VIDEO_URL, "desired_increase": "4"})
    assert parsed is not None
    assert parsed.model_dump()["desired_increase"] == "4"


def test_bria_video_erase_keypoints_accepts_empty_list_without_an_openapi_minimum() -> None:
    parsed = validate_parameters(ERASE_APP_IDS[0], {"video_url": VIDEO_URL, "keypoints": []})
    assert parsed is not None
    assert parsed.model_dump()["keypoints"] == []

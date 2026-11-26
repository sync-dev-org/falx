from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx import models
from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

VIDEO_URL = "https://example.com/source.mp4"
IMAGE_URL = "https://example.com/source.png"
DENOISE_VIDEO = "topaz/denoise/video"
HDR_VIDEO = "topaz/sdr-to-hdr/video"
CREATIVE_VIDEO = "topaz/upscale/video/creative"
GENERATIVE_VIDEO = "topaz/upscale/video/generative"
PRECISION_VIDEO = "topaz/upscale/video/precision"
IMAGE_MODELS = {
    "topaz/adjust/image": ["Adjust V2", "White Balance", "Colorize"],
    "topaz/denoise/image": ["Normal", "Strong", "Extreme", "Denoise Max"],
    "topaz/restore/image": ["Recover 3", "Dust-Scratch V2"],
    "topaz/sharpen/image": [
        "Standard",
        "Strong",
        "Lens Blur V2",
        "Motion Blur",
        "Natural",
        "Refocus",
        "Wildlife",
        "Portrait",
        "Auto Sharpen",
        "Super Focus V3",
        "Super Focus V2",
    ],
}
VIDEO_MODELS = {
    DENOISE_VIDEO: ["Nyx", "Nyx Fast", "Nyx XL", "Nyx HF"],
    GENERATIVE_VIDEO: [
        "Starlight Precise 2.6",
        "Starlight HQ",
        "Starlight Mini",
        "Starlight Sharp",
        "Starlight Fast 2",
    ],
    PRECISION_VIDEO: [
        "Proteus",
        "Proteus Natural",
        "Iris",
        "Iris Low Quality",
        "Dione DV",
        "Dione TV",
        "Dione Robust",
        "Dione Dehalo",
        "Dione Robust Dehalo",
        "Artemis High Quality",
        "Artemis Medium Quality",
        "Artemis Low Quality",
        "Artemis Strong Halo",
        "Artemis Medium Halo",
        "Artemis Aliasing & Moire",
        "Gaia HQ",
        "Gaia CG",
        "Gaia 2",
        "Rhea",
        "Theia Fine Tune Detail",
        "Theia Fine Tune Fidelity",
    ],
}
CLASS_NAMES = {
    DENOISE_VIDEO: "TopazDenoiseVideoConfig",
    HDR_VIDEO: "TopazSdrToHdrVideoConfig",
    CREATIVE_VIDEO: "TopazUpscaleVideoCreativeConfig",
    GENERATIVE_VIDEO: "TopazUpscaleVideoGenerativeConfig",
    PRECISION_VIDEO: "TopazUpscaleVideoPrecisionConfig",
    "topaz/adjust/image": "TopazAdjustImageConfig",
    "topaz/denoise/image": "TopazDenoiseImageConfig",
    "topaz/restore/image": "TopazRestoreImageConfig",
    "topaz/sharpen/image": "TopazSharpenImageConfig",
}
DEFAULTS = {
    DENOISE_VIDEO: {
        "video_url": VIDEO_URL,
        "enable_safety_checker": True,
        "model": "Nyx",
        "upscale_factor": 1,
        "noise": None,
        "compression": None,
        "halo": None,
        "H264_output": False,
    },
    HDR_VIDEO: {
        "video_url": VIDEO_URL,
        "enable_safety_checker": True,
        "output_format": "mp4",
    },
    CREATIVE_VIDEO: {
        "video_url": VIDEO_URL,
        "enable_safety_checker": True,
        "prompt": None,
        "creativity": 0.5,
        "realism": None,
        "sharp": None,
        "upscale_factor": 2,
        "target_fps": None,
        "H264_output": False,
    },
    GENERATIVE_VIDEO: {
        "video_url": VIDEO_URL,
        "enable_safety_checker": True,
        "model": "Starlight Precise 2.6",
        "upscale_factor": 2,
        "target_fps": None,
        "softness": None,
        "H264_output": False,
    },
    PRECISION_VIDEO: {
        "video_url": VIDEO_URL,
        "enable_safety_checker": True,
        "model": "Proteus",
        "upscale_factor": 2,
        "target_fps": None,
        "compression": None,
        "noise": None,
        "halo": None,
        "grain": None,
        "recover_detail": None,
        "H264_output": False,
    },
    **{
        app_id: {
            "image_url": IMAGE_URL,
            "output_format": "jpeg",
            "model": choices[0],
            "enable_safety_checker": True,
        }
        for app_id, choices in IMAGE_MODELS.items()
    },
}
NUMERIC_LIMITS = [
    (DENOISE_VIDEO, "upscale_factor", 1, 4),
    (DENOISE_VIDEO, "noise", 0, 1),
    (DENOISE_VIDEO, "compression", 0, 1),
    (DENOISE_VIDEO, "halo", 0, 1),
    (CREATIVE_VIDEO, "creativity", 0, 1),
    (CREATIVE_VIDEO, "realism", 0, 1),
    (CREATIVE_VIDEO, "sharp", 0, 1),
    (CREATIVE_VIDEO, "upscale_factor", 1, 4),
    (CREATIVE_VIDEO, "target_fps", 16, 60),
    (GENERATIVE_VIDEO, "upscale_factor", 1, 4),
    (GENERATIVE_VIDEO, "target_fps", 16, 60),
    (GENERATIVE_VIDEO, "softness", 1, 5),
    (PRECISION_VIDEO, "upscale_factor", 1, 4),
    (PRECISION_VIDEO, "target_fps", 16, 60),
    (PRECISION_VIDEO, "compression", 0, 1),
    (PRECISION_VIDEO, "noise", 0, 1),
    (PRECISION_VIDEO, "halo", 0, 1),
    (PRECISION_VIDEO, "grain", 0, 0.1),
    (PRECISION_VIDEO, "recover_detail", 0, 1),
]
ENUMS = [
    *[(app_id, "model", values) for app_id, values in {**VIDEO_MODELS, **IMAGE_MODELS}.items()],
    (HDR_VIDEO, "output_format", ["mp4", "prores"]),
    *[(app_id, "output_format", ["jpeg", "png"]) for app_id in IMAGE_MODELS],
]


def required_parameters(app_id: str) -> dict[str, object]:
    return {"image_url": IMAGE_URL} if app_id in IMAGE_MODELS else {"video_url": VIDEO_URL}


@pytest.mark.parametrize("app_id", CLASS_NAMES)
def test_topaz_processing_registers_public_configs_with_api_defaults(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    assert config_class.__name__ == CLASS_NAMES[app_id]
    assert getattr(models, CLASS_NAMES[app_id]) is config_class
    assert CLASS_NAMES[app_id] in models.__all__
    config = validate_parameters(app_id, required_parameters(app_id))
    assert isinstance(config, config_class)
    assert config.model_dump() == {"app_id": app_id, **DEFAULTS[app_id]}
    assert config_class.random_seed_field is None
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)
    assert isinstance(
        adapter.validate_python({"app_id": app_id, **required_parameters(app_id)}),
        config_class,
    )


@pytest.mark.parametrize("app_id", CLASS_NAMES)
def test_topaz_processing_requires_input_url_and_rejects_unknown_fields(app_id: str) -> None:
    url_field = next(iter(required_parameters(app_id)))
    with pytest.raises(ValidationError, match=url_field):
        validate_parameters(app_id, {})
    with pytest.raises(ValidationError, match="unexpected"):
        validate_parameters(app_id, {**required_parameters(app_id), "unexpected": True})


@pytest.mark.parametrize("app_id", IMAGE_MODELS)
def test_topaz_image_processing_requires_nonempty_input_url(app_id: str) -> None:
    with pytest.raises(ValidationError, match="image_url"):
        validate_parameters(app_id, {"image_url": ""})


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [(app_id, field, value) for app_id, field, values in ENUMS for value in values],
)
def test_topaz_processing_accepts_all_api_enum_values(
    app_id: str,
    field: str,
    value: str,
) -> None:
    config = validate_parameters(app_id, {**required_parameters(app_id), field: value})
    assert config is not None
    assert getattr(config, field) == value


@pytest.mark.parametrize(("app_id", "field", "values"), ENUMS)
def test_topaz_processing_rejects_unknown_api_enum_values(
    app_id: str,
    field: str,
    values: list[str],
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**required_parameters(app_id), field: "unknown"})


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [
        (app_id, field, value)
        for app_id, field, low, high in NUMERIC_LIMITS
        for value in (low, high)
    ],
)
def test_topaz_video_processing_accepts_numeric_boundaries(
    app_id: str,
    field: str,
    value: float,
) -> None:
    config = validate_parameters(app_id, {"video_url": VIDEO_URL, field: value})
    assert config is not None
    assert getattr(config, field) == value


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [
        (app_id, field, value)
        for app_id, field, low, high in NUMERIC_LIMITS
        for value in (low - 1, high + 1)
    ],
)
def test_topaz_video_processing_rejects_values_outside_numeric_limits(
    app_id: str,
    field: str,
    value: float,
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {"video_url": VIDEO_URL, field: value})


@pytest.mark.parametrize("app_id", [CREATIVE_VIDEO, GENERATIVE_VIDEO, PRECISION_VIDEO])
def test_topaz_upscale_video_requires_integral_target_fps(app_id: str) -> None:
    with pytest.raises(ValidationError, match="target_fps"):
        validate_parameters(app_id, {"video_url": VIDEO_URL, "target_fps": 29.5})


def test_topaz_precision_video_requires_grain_steps_of_one_hundredth() -> None:
    config = validate_parameters(PRECISION_VIDEO, {"video_url": VIDEO_URL, "grain": 0.03})
    assert config is not None
    assert config.grain == 0.03
    with pytest.raises(ValidationError, match="grain"):
        validate_parameters(PRECISION_VIDEO, {"video_url": VIDEO_URL, "grain": 0.035})


def test_topaz_creative_video_limits_prompt_to_1024_characters() -> None:
    prompt = "x" * 1024
    config = validate_parameters(CREATIVE_VIDEO, {"video_url": VIDEO_URL, "prompt": prompt})
    assert config is not None
    assert config.prompt == prompt
    with pytest.raises(ValidationError, match="prompt"):
        validate_parameters(CREATIVE_VIDEO, {"video_url": VIDEO_URL, "prompt": prompt + "x"})


@pytest.mark.parametrize("app_id", CLASS_NAMES)
def test_topaz_processing_preserves_optional_nulls_and_boolean_controls(app_id: str) -> None:
    parameters = {
        **required_parameters(app_id),
        **{field: None for field, value in DEFAULTS[app_id].items() if value is None},
        "enable_safety_checker": False,
    }
    if "H264_output" in DEFAULTS[app_id]:
        parameters["H264_output"] = True
    config = validate_parameters(app_id, parameters)
    assert config is not None
    assert config.model_dump(exclude_unset=True) == {"app_id": app_id, **parameters}


@pytest.mark.parametrize(
    ("app_id", "parameters", "field"),
    [
        (HDR_VIDEO, {"H264_output": True}, "H264_output"),
        (CREATIVE_VIDEO, {"model": "Astra 2"}, "model"),
        (DENOISE_VIDEO, {"target_fps": 30}, "target_fps"),
    ],
)
def test_topaz_processing_keeps_endpoint_specific_fields_separate(
    app_id: str,
    parameters: dict[str, object],
    field: str,
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**required_parameters(app_id), **parameters})

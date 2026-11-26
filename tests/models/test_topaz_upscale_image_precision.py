from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SUPPORTED_APP_IDS, TopazUpscaleImagePrecisionConfig, validate_parameters

APP_ID = "topaz/upscale/image/precision"


def test_topaz_upscale_image_precision_accepts_schema_defaults() -> None:
    config = TopazUpscaleImagePrecisionConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.png",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "image_url": "https://example.com/source.png",
        "model": "Standard V2",
        "upscale_factor": 2,
        "crop_to_fill": False,
        "output_format": "jpeg",
        "subject_detection": "All",
        "face_enhancement": True,
        "face_enhancement_creativity": 0,
        "face_enhancement_strength": 0.8,
        "sharpen": None,
        "denoise": None,
        "fix_compression": None,
        "strength": None,
    }


def test_topaz_upscale_image_precision_accepts_all_fields() -> None:
    config = TopazUpscaleImagePrecisionConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.png",
        model="Text Refine",
        upscale_factor=4,
        crop_to_fill=True,
        output_format="png",
        subject_detection="Background",
        face_enhancement=False,
        face_enhancement_creativity=1,
        face_enhancement_strength=0,
        sharpen=1,
        denoise=0,
        fix_compression=0.5,
        strength=0.01,
    )

    assert config.model == "Text Refine"
    assert config.subject_detection == "Background"
    assert config.fix_compression == 0.5
    assert config.strength == 0.01


def test_topaz_upscale_image_precision_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS

    validated = validate_parameters(APP_ID, {"image_url": "https://example.com/source.png"})

    assert isinstance(validated, TopazUpscaleImagePrecisionConfig)


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "image_url"),
        ({"image_url": ""}, "image_url"),
        ({"image_url": "x", "model": "Standard V3"}, "model"),
        ({"image_url": "x", "upscale_factor": 0.5}, "upscale_factor"),
        ({"image_url": "x", "upscale_factor": 4.5}, "upscale_factor"),
        ({"image_url": "x", "subject_detection": "Subject"}, "subject_detection"),
        (
            {"image_url": "x", "face_enhancement_creativity": -0.1},
            "face_enhancement_creativity",
        ),
        (
            {"image_url": "x", "face_enhancement_strength": 1.1},
            "face_enhancement_strength",
        ),
        ({"image_url": "x", "sharpen": -0.1}, "sharpen"),
        ({"image_url": "x", "denoise": 1.1}, "denoise"),
        ({"image_url": "x", "fix_compression": 1.1}, "fix_compression"),
        ({"image_url": "x", "strength": 0}, "strength"),
        ({"image_url": "x", "output_format": "webp"}, "output_format"),
        ({"image_url": "x", "unexpected": True}, "unexpected"),
    ],
)
def test_topaz_upscale_image_precision_rejects_invalid_parameters(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        validate_parameters(APP_ID, parameters)

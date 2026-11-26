from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SUPPORTED_APP_IDS, TopazUpscaleImageGenerativeConfig, validate_parameters

APP_ID = "topaz/upscale/image/generative"


def test_topaz_upscale_image_generative_accepts_schema_defaults() -> None:
    config = TopazUpscaleImageGenerativeConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.png",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "image_url": "https://example.com/source.png",
        "model": "Wonder 3",
        "upscale_factor": 2,
        "crop_to_fill": False,
        "output_format": "jpeg",
        "subject_detection": "All",
        "face_enhancement": True,
        "face_enhancement_creativity": 0,
        "face_enhancement_strength": 0.8,
        "enhancement_strength": None,
        "creativity": None,
        "texture": None,
        "prompt": None,
        "autoprompt": None,
        "sharpen": None,
        "denoise": None,
        "detail": None,
        "enable_safety_checker": True,
    }


def test_topaz_upscale_image_generative_accepts_all_fields() -> None:
    config = TopazUpscaleImageGenerativeConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.png",
        model="Redefine",
        upscale_factor=4,
        crop_to_fill=True,
        output_format="png",
        subject_detection="Foreground",
        face_enhancement=False,
        face_enhancement_creativity=1,
        face_enhancement_strength=0,
        enhancement_strength="high",
        creativity=6,
        texture=5,
        prompt="Restore the carved details.",
        autoprompt=True,
        sharpen=1,
        denoise=0,
        detail=1,
    )

    assert config.model == "Redefine"
    assert config.enhancement_strength == "high"
    assert config.creativity == 6
    assert config.detail == 1


def test_topaz_upscale_image_generative_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS

    validated = validate_parameters(APP_ID, {"image_url": "https://example.com/source.png"})

    assert isinstance(validated, TopazUpscaleImageGenerativeConfig)


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "image_url"),
        ({"image_url": ""}, "image_url"),
        ({"image_url": "x", "model": "unknown"}, "model"),
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
        ({"image_url": "x", "enhancement_strength": "maximum"}, "enhancement_strength"),
        ({"image_url": "x", "creativity": 0}, "creativity"),
        ({"image_url": "x", "texture": 6}, "texture"),
        ({"image_url": "x", "prompt": "x" * 1025}, "prompt"),
        ({"image_url": "x", "sharpen": -0.1}, "sharpen"),
        ({"image_url": "x", "denoise": 1.1}, "denoise"),
        ({"image_url": "x", "detail": -0.1}, "detail"),
        ({"image_url": "x", "output_format": "webp"}, "output_format"),
        ({"image_url": "x", "unexpected": True}, "unexpected"),
    ],
)
def test_topaz_upscale_image_generative_rejects_invalid_parameters(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        validate_parameters(APP_ID, parameters)

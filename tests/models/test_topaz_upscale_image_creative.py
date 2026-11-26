from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SUPPORTED_APP_IDS, TopazUpscaleImageCreativeConfig, validate_parameters

APP_ID = "topaz/upscale/image/creative"


def test_topaz_upscale_image_creative_accepts_schema_defaults() -> None:
    config = TopazUpscaleImageCreativeConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.png",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "image_url": "https://example.com/source.png",
        "model": "Bloom 2",
        "upscale_factor": 2,
        "autoprompt": None,
        "creativity": None,
        "color_preservation": None,
        "crop_to_fill": False,
        "output_format": "jpeg",
    }


def test_topaz_upscale_image_creative_accepts_all_fields() -> None:
    config = TopazUpscaleImageCreativeConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.png",
        model="Bloom Realism",
        upscale_factor=4,
        autoprompt=False,
        creativity=9,
        color_preservation=True,
        crop_to_fill=True,
        output_format="png",
    )

    assert config.model == "Bloom Realism"
    assert config.upscale_factor == 4
    assert config.creativity == 9
    assert config.output_format == "png"


def test_topaz_upscale_image_creative_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS

    validated = validate_parameters(APP_ID, {"image_url": "https://example.com/source.png"})

    assert isinstance(validated, TopazUpscaleImageCreativeConfig)


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "image_url"),
        ({"image_url": ""}, "image_url"),
        ({"image_url": "x", "model": "Bloom 3"}, "model"),
        ({"image_url": "x", "upscale_factor": 0.5}, "upscale_factor"),
        ({"image_url": "x", "upscale_factor": 4.5}, "upscale_factor"),
        ({"image_url": "x", "creativity": 0}, "creativity"),
        ({"image_url": "x", "creativity": 10}, "creativity"),
        ({"image_url": "x", "output_format": "webp"}, "output_format"),
        ({"image_url": "x", "unexpected": True}, "unexpected"),
    ],
)
def test_topaz_upscale_image_creative_rejects_invalid_parameters(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        validate_parameters(APP_ID, parameters)

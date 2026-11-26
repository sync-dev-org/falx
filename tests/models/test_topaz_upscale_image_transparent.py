from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SUPPORTED_APP_IDS, TopazUpscaleImageTransparentConfig, validate_parameters

APP_ID = "topaz/upscale/image/transparent"


def test_topaz_upscale_image_transparent_accepts_schema_defaults() -> None:
    config = TopazUpscaleImageTransparentConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.png",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "image_url": "https://example.com/source.png",
        "output_format": "png",
    }


def test_topaz_upscale_image_transparent_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS

    validated = validate_parameters(APP_ID, {"image_url": "https://example.com/source.png"})

    assert isinstance(validated, TopazUpscaleImageTransparentConfig)


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "image_url"),
        ({"image_url": ""}, "image_url"),
        ({"image_url": "x", "output_format": "jpeg"}, "output_format"),
        ({"image_url": "x", "unexpected": True}, "unexpected"),
    ],
)
def test_topaz_upscale_image_transparent_rejects_invalid_parameters(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        validate_parameters(APP_ID, parameters)

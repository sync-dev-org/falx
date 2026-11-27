from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import RecraftVectorizeProConfig

APP_ID = "recraft/vectorize/pro"
IMAGE_URL = "https://example.com/input.png"


def test_recraft_vectorize_pro_accepts_required_image_with_api_defaults() -> None:
    config = RecraftVectorizeProConfig(app_id=APP_ID, image_url=IMAGE_URL)

    assert config.model_dump() == {
        "app_id": APP_ID,
        "image_url": IMAGE_URL,
        "enable_safety_checker": True,
        "shape_stacking": "hierarchical",
    }
    assert set(config.model_json_schema()["required"]) == {"app_id", "image_url"}


@pytest.mark.parametrize("shape_stacking", ["hierarchical", "cut_out"])
def test_recraft_vectorize_pro_accepts_layering_modes(shape_stacking: str) -> None:
    config = RecraftVectorizeProConfig(
        app_id=APP_ID,
        image_url=IMAGE_URL,
        enable_safety_checker=False,
        shape_stacking=shape_stacking,
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "image_url": IMAGE_URL,
        "enable_safety_checker": False,
        "shape_stacking": shape_stacking,
    }


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "image_url"),
        ({"image_url": None}, "image_url"),
        ({"shape_stacking": "flat"}, "shape_stacking"),
        ({"shape_stacking": None}, "shape_stacking"),
        ({"enable_safety_checker": None}, "enable_safety_checker"),
        ({"unexpected": True}, "unexpected"),
    ],
)
def test_recraft_vectorize_pro_rejects_invalid_parameters(
    parameters: dict[str, object], needle: str
) -> None:
    payload = {"app_id": APP_ID, "image_url": IMAGE_URL, **parameters}
    if not parameters:
        payload.pop("image_url")
    with pytest.raises(ValidationError, match=needle):
        RecraftVectorizeProConfig.model_validate(payload)

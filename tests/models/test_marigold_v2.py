from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import MarigoldV2Config, MarigoldV2ImageSize

APP_ID = "fal-ai/marigold-v2"
IMAGE_URL = "https://example.com/input.png"


def test_marigold_v2_accepts_required_image_with_api_defaults() -> None:
    config = MarigoldV2Config(app_id=APP_ID, image_url=IMAGE_URL)

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prediction_type": "depth",
        "image_url": IMAGE_URL,
        "image_size": None,
        "seed": None,
        "enable_safety_checker": True,
    }


def test_marigold_v2_accepts_all_fields_and_structured_size_boundaries() -> None:
    config = MarigoldV2Config(
        app_id=APP_ID,
        prediction_type="normals",
        image_url=IMAGE_URL,
        image_size={"width": 14142, "height": 1},
        seed=-1,
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prediction_type": "normals",
        "image_url": IMAGE_URL,
        "image_size": {"width": 14142, "height": 1},
        "seed": -1,
        "enable_safety_checker": False,
    }
    assert MarigoldV2ImageSize().model_dump() == {"width": 512, "height": 512}


@pytest.mark.parametrize("prediction_type", ["depth", "see-through-depth", "normals", "albedo"])
def test_marigold_v2_accepts_prediction_types(prediction_type: str) -> None:
    config = MarigoldV2Config(app_id=APP_ID, image_url=IMAGE_URL, prediction_type=prediction_type)

    assert config.prediction_type == prediction_type


@pytest.mark.parametrize(
    "image_size",
    [
        None,
        "square_hd",
        "square",
        "portrait_4_3",
        "portrait_16_9",
        "landscape_4_3",
        "landscape_16_9",
    ],
)
def test_marigold_v2_accepts_size_presets_and_null(image_size: str | None) -> None:
    config = MarigoldV2Config(app_id=APP_ID, image_url=IMAGE_URL, image_size=image_size)

    assert config.image_size == image_size


def test_marigold_v2_preserves_nullable_defaults_and_size_constraints_in_schema() -> None:
    schema = MarigoldV2Config.model_json_schema()

    assert set(schema["required"]) == {"app_id", "image_url"}
    assert schema["properties"]["image_size"]["default"] is None
    assert schema["properties"]["seed"]["default"] is None
    for dimension in ("width", "height"):
        size_property = schema["$defs"]["MarigoldV2ImageSize"]["properties"][dimension]
        assert size_property["default"] == 512
        assert size_property["exclusiveMinimum"] == 0
        assert size_property["maximum"] == 14142


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "image_url"),
        ({"image_url": None}, "image_url"),
        ({"prediction_type": "disparity"}, "prediction_type"),
        ({"image_size": "auto"}, "image_size"),
        ({"image_size": {"width": 0}}, "width"),
        ({"image_size": {"width": 14143}}, "width"),
        ({"image_size": {"height": 0}}, "height"),
        ({"image_size": {"height": 14143}}, "height"),
        ({"image_size": {"unit": "px"}}, "unit"),
        ({"seed": "random"}, "seed"),
        ({"enable_safety_checker": None}, "enable_safety_checker"),
        ({"unexpected": True}, "unexpected"),
    ],
)
def test_marigold_v2_rejects_invalid_parameters(parameters: dict[str, object], needle: str) -> None:
    payload = {"app_id": APP_ID, "image_url": IMAGE_URL, **parameters}
    if not parameters:
        payload.pop("image_url")
    with pytest.raises(ValidationError, match=needle):
        MarigoldV2Config.model_validate(payload)

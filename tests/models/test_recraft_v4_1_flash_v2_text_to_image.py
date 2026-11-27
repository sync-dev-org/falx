from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    RecraftV41FlashV2ImageSize,
    RecraftV41FlashV2RGBColor,
    RecraftV41FlashV2TextToImageConfig,
)

APP_ID = "recraft/v4.1/flash/v2/text-to-image"


def test_recraft_flash_v2_accepts_required_prompt_with_api_defaults() -> None:
    config = RecraftV41FlashV2TextToImageConfig(app_id=APP_ID, prompt="A fishing village.")

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A fishing village.",
        "image_size": "square_hd",
        "colors": [],
        "background_color": None,
        "enable_safety_checker": True,
    }


def test_recraft_flash_v2_accepts_custom_size_and_nested_colors() -> None:
    config = RecraftV41FlashV2TextToImageConfig(
        app_id=APP_ID,
        prompt="x" * 10000,
        image_size={"width": 1, "height": 14142},
        colors=[{"r": 255}, {"g": 255}, {"b": 255}, {}],
        background_color={"r": 255, "g": 255, "b": 255},
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "x" * 10000,
        "image_size": {"width": 1, "height": 14142},
        "colors": [
            {"r": 255, "g": 0, "b": 0},
            {"r": 0, "g": 255, "b": 0},
            {"r": 0, "g": 0, "b": 255},
            {"r": 0, "g": 0, "b": 0},
        ],
        "background_color": {"r": 255, "g": 255, "b": 255},
        "enable_safety_checker": False,
    }
    assert RecraftV41FlashV2ImageSize().model_dump() == {"width": 512, "height": 512}


@pytest.mark.parametrize(
    "image_size",
    ["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"],
)
def test_recraft_flash_v2_accepts_size_presets(image_size: str) -> None:
    config = RecraftV41FlashV2TextToImageConfig(app_id=APP_ID, prompt="x", image_size=image_size)

    assert config.image_size == image_size


def test_recraft_flash_v2_uses_independent_color_defaults() -> None:
    first = RecraftV41FlashV2TextToImageConfig(app_id=APP_ID, prompt="x")
    first.colors.append(RecraftV41FlashV2RGBColor(r=255))
    second = RecraftV41FlashV2TextToImageConfig(app_id=APP_ID, prompt="x")

    assert second.colors == []


def test_recraft_flash_v2_schema_preserves_prompt_and_color_constraints() -> None:
    schema = RecraftV41FlashV2TextToImageConfig.model_json_schema()

    assert set(schema["required"]) == {"app_id", "prompt"}
    assert schema["properties"]["prompt"]["minLength"] == 1
    assert schema["properties"]["prompt"]["maxLength"] == 10000
    assert schema["properties"]["background_color"]["default"] is None
    for channel in ("r", "g", "b"):
        color_property = schema["$defs"]["RecraftV41FlashV2RGBColor"]["properties"][channel]
        assert color_property["default"] == 0
        assert color_property["minimum"] == 0
        assert color_property["maximum"] == 255


@pytest.mark.parametrize("field", ["colors", "background_color"])
@pytest.mark.parametrize("channel", ["r", "g", "b"])
@pytest.mark.parametrize("value", [-1, 256])
def test_recraft_flash_v2_rejects_out_of_range_color_channels(
    field: str, channel: str, value: int
) -> None:
    color = {channel: value}
    with pytest.raises(ValidationError, match=channel):
        RecraftV41FlashV2TextToImageConfig.model_validate(
            {"app_id": APP_ID, "prompt": "x", field: [color] if field == "colors" else color}
        )


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "prompt"),
        ({"prompt": ""}, "prompt"),
        ({"prompt": "x" * 10001}, "prompt"),
        ({"image_size": "auto"}, "image_size"),
        ({"image_size": None}, "image_size"),
        ({"image_size": {"width": 0}}, "width"),
        ({"image_size": {"height": 14143}}, "height"),
        ({"colors": None}, "colors"),
        ({"colors": [{"alpha": 255}]}, "alpha"),
        ({"background_color": "white"}, "background_color"),
        ({"enable_safety_checker": None}, "enable_safety_checker"),
        ({"seed": 42}, "seed"),
    ],
)
def test_recraft_flash_v2_rejects_invalid_parameters(
    parameters: dict[str, object], needle: str
) -> None:
    payload = {"app_id": APP_ID, "prompt": "A fishing village.", **parameters}
    if not parameters:
        payload.pop("prompt")
    with pytest.raises(ValidationError, match=needle):
        RecraftV41FlashV2TextToImageConfig.model_validate(payload)

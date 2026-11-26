from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import config_class_for_app_id, validate_parameters

TEXT = "bytedance/seedream/v5/pro/text-to-image"
EDIT = "bytedance/seedream/v5/pro/edit"
LAYERIZE = "bytedance/seedream/v5/pro/layerize"
APP_IDS = (TEXT, EDIT, LAYERIZE)


def _parameters(app_id: str) -> dict[str, object]:
    if app_id == LAYERIZE:
        return {"image_url": "https://example.com/input.png"}
    parameters: dict[str, object] = {"prompt": "A ceramic vase."}
    if app_id == EDIT:
        parameters["image_urls"] = ["https://example.com/input.png"]
    return parameters


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("watermark", (False, True))
def test_seedream_v5_pro_preserves_watermark_in_request(app_id: str, watermark: bool) -> None:
    config = validate_parameters(app_id, {**_parameters(app_id), "watermark": watermark})

    assert config is not None
    assert config.model_dump(exclude={"app_id"})["watermark"] is watermark


@pytest.mark.parametrize("app_id", (TEXT, EDIT))
@pytest.mark.parametrize("mode", ("standard", "fast"))
def test_seedream_v5_pro_preserves_prompt_optimization_in_request(app_id: str, mode: str) -> None:
    config = validate_parameters(app_id, {**_parameters(app_id), "enhance_prompt_mode": mode})

    assert config is not None
    assert config.model_dump(exclude={"app_id"})["enhance_prompt_mode"] == mode


@pytest.mark.parametrize("app_id", (TEXT, EDIT))
def test_seedream_v5_pro_accepts_one_and_a_half_k_resolution(app_id: str) -> None:
    config = validate_parameters(app_id, {**_parameters(app_id), "image_size": "auto_1.5K"})

    assert config is not None
    assert config.model_dump(exclude={"app_id"})["image_size"] == "auto_1.5K"


@pytest.mark.parametrize("background", ("opaque", "transparent"))
def test_seedream_v5_pro_edit_preserves_background_in_request(background: str) -> None:
    config = validate_parameters(EDIT, {**_parameters(EDIT), "background": background})

    assert config is not None
    assert config.model_dump(exclude={"app_id"})["background"] == background


@pytest.mark.parametrize("output_format", ("jpeg", "png"))
def test_seedream_v5_pro_layerize_preserves_base_image_format(output_format: str) -> None:
    config = validate_parameters(
        LAYERIZE, {**_parameters(LAYERIZE), "output_format": output_format}
    )

    assert config is not None
    assert config.model_dump(exclude={"app_id"})["output_format"] == output_format


@pytest.mark.parametrize("app_id", APP_IDS)
def test_seedream_v5_pro_new_options_are_optional_and_have_api_defaults(app_id: str) -> None:
    config = validate_parameters(app_id, _parameters(app_id))
    config_class = config_class_for_app_id(app_id)
    assert config is not None
    assert config_class is not None
    parameters = config.model_dump(exclude={"app_id"})
    schema = config_class.model_json_schema()
    defaults: dict[str, object] = {"watermark": False, "enhance_prompt_mode": "standard"}
    if app_id == EDIT:
        defaults["background"] = "opaque"
    if app_id == LAYERIZE:
        defaults["output_format"] = "png"
    for field, default in defaults.items():
        assert field not in schema["required"]
        assert schema["properties"][field]["default"] == default
        assert parameters[field] == default


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [
        (TEXT, "enhance_prompt_mode", "quality"),
        (EDIT, "enhance_prompt_mode", "quality"),
        (EDIT, "background", "auto"),
        (LAYERIZE, "output_format", "webp"),
    ],
)
def test_seedream_v5_pro_rejects_values_outside_new_option_enums(
    app_id: str, field: str, value: str
) -> None:
    with pytest.raises(ValidationError, match=field) as error:
        validate_parameters(app_id, {**_parameters(app_id), field: value})
    assert error.value.errors()[0]["type"] == "literal_error"
    assert error.value.errors()[0]["loc"][-1] == field

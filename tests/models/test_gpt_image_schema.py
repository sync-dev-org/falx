from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import config_class_for_app_id, validate_parameters

APP_IDS = [
    "openai/gpt-image-2",
    "openai/gpt-image-2/edit",
    "openai/gpt-image-2.5/flare/text-to-image",
    "openai/gpt-image-2.5/flare/edit",
    "openai/gpt-image-2.5/sunburst/text-to-image",
    "openai/gpt-image-2.5/sunburst/edit",
]


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("image_size", "expected"),
    [
        ({}, {"width": 512, "height": 512}),
        ({"width": 14142}, {"width": 14142, "height": 512}),
        ({"height": 1}, {"width": 512, "height": 1}),
    ],
)
def test_gpt_image_accepts_custom_size_defaults_and_boundaries(
    app_id: str, image_size: dict[str, int], expected: dict[str, int]
) -> None:
    parameters: dict[str, object] = {"prompt": "a cat", "image_size": image_size}
    if app_id.endswith("/edit"):
        parameters["image_urls"] = ["https://example.com/input.png"]

    config = validate_parameters(app_id, parameters)

    assert config is not None
    assert config.model_dump()["image_size"] == expected


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("dimension", ["width", "height"])
@pytest.mark.parametrize("value", [-1, 0, 14143])
def test_gpt_image_rejects_custom_size_outside_api_bounds(
    app_id: str, dimension: str, value: int
) -> None:
    image_size = {"width": 512, "height": 512, dimension: value}
    parameters: dict[str, object] = {"prompt": "a cat", "image_size": image_size}
    if app_id.endswith("/edit"):
        parameters["image_urls"] = ["https://example.com/input.png"]

    with pytest.raises(ValidationError, match=dimension):
        validate_parameters(app_id, parameters)


@pytest.mark.parametrize("app_id", APP_IDS)
def test_gpt_image_schema_examples_include_current_api_defaults(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])

    assert result.exit_code == 0, result.output
    payload = YAML(typ="safe").load(result.stdout)
    assert payload["app_id"] == app_id
    parameters = payload["parameters"]
    assert parameters["background"] == "auto"
    assert parameters["output_compression"] is None
    assert parameters["enable_safety_checker"] is True
    config = validate_parameters(app_id, parameters)
    assert config is not None
    assert config.model_dump(exclude={"app_id"}) == parameters


@pytest.mark.parametrize("app_id", APP_IDS)
def test_gpt_image_schema_describes_optional_custom_size_dimensions(app_id: str) -> None:
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    image_size = config_class.model_json_schema()["$defs"]["ImageSize"]

    assert image_size.get("required", []) == []
    for dimension in ("width", "height"):
        field = image_size["properties"][dimension]
        assert field["default"] == 512
        assert field["exclusiveMinimum"] == 0
        assert field["maximum"] == 14142

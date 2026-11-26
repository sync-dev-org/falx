from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import config_class_for_app_id, validate_parameters

BOOLEAN_INPUTS = [
    ("sonilo/v1.1/video-to-sound-effects", "video_url", "keep_speech_vocal", False),
    ("topaz/deblur/video", "video_url", "enable_safety_checker", True),
    ("topaz/interpolate/video", "video_url", "enable_safety_checker", True),
    ("topaz/upscale/image/creative", "image_url", "enable_safety_checker", True),
    ("topaz/upscale/image/generative", "image_url", "enable_safety_checker", True),
    ("topaz/upscale/image/precision", "image_url", "enable_safety_checker", True),
    ("topaz/upscale/image/transparent", "image_url", "enable_safety_checker", True),
]


@pytest.mark.parametrize(("app_id", "url_field", "field", "default"), BOOLEAN_INPUTS)
def test_topaz_and_sonilo_boolean_inputs_preserve_defaults_and_explicit_values(
    app_id: str, url_field: str, field: str, default: bool
) -> None:
    parameters = {url_field: "https://example.com/input"}
    config = validate_parameters(app_id, parameters)
    assert config is not None
    assert config.model_dump(exclude={"app_id"}, exclude_none=True)[field] is default

    schema = config_class_for_app_id(app_id).model_json_schema()
    assert schema["properties"][field]["type"] == "boolean"
    assert schema["properties"][field]["default"] is default
    assert field not in schema["required"]

    for value in (True, False):
        config = validate_parameters(app_id, {**parameters, field: value})
        assert config is not None
        assert config.model_dump(exclude={"app_id"}, exclude_none=True)[field] is value


@pytest.mark.parametrize(("app_id", "url_field", "field", "default"), BOOLEAN_INPUTS)
def test_topaz_and_sonilo_boolean_inputs_reject_null_and_non_boolean_values(
    app_id: str, url_field: str, field: str, default: bool
) -> None:
    for value in (None, 2, "enabled"):
        with pytest.raises(ValidationError, match=field):
            validate_parameters(app_id, {url_field: "https://example.com/input", field: value})


@pytest.mark.parametrize(("app_id", "url_field", "field", "default"), BOOLEAN_INPUTS)
def test_topaz_and_sonilo_schema_examples_include_boolean_defaults(
    app_id: str, url_field: str, field: str, default: bool
) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    job = YAML(typ="safe").load(result.stdout)
    assert job["app_id"] == app_id
    assert job["parameters"][url_field] == "https://example.com/input"
    assert job["parameters"][field] is default
    assert validate_parameters(app_id, job["parameters"]) is not None


@pytest.mark.parametrize(
    ("app_id", "model"),
    [
        ("topaz/upscale/image/generative", "Wonder 4"),
        ("topaz/upscale/image/precision", "Faces"),
    ],
)
def test_topaz_upscale_image_accepts_new_models(app_id: str, model: str) -> None:
    config = validate_parameters(app_id, {"image_url": "https://example.com/input", "model": model})

    assert config is not None
    assert config.model_dump(exclude={"app_id"}, exclude_none=True)["model"] == model
    schema = config_class_for_app_id(app_id).model_json_schema()
    assert model in schema["properties"]["model"]["enum"]

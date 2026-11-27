from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

TEXT = "ideogram/vector/text-to-vector"
IMAGE = "ideogram/vector/image-to-vector"
URL = "https://example.com/image.png"


def config(app_id: str, **parameters: object):
    assert app_id in SUPPORTED_APP_IDS
    defaults = {"prompt": "A playful cat logo."} if app_id == TEXT else {"image_url": URL}
    result = validate_parameters(app_id, {**defaults, **parameters})
    assert result is not None
    return result


@pytest.mark.parametrize("app_id", [TEXT, IMAGE])
def test_vector_registers_and_preserves_defaults(app_id: str) -> None:
    result = config(app_id)
    expected = (
        {
            "prompt": "A playful cat logo.",
            "quality": "medium",
            "num_images": 1,
            "aspect_ratio": "auto",
            "seed": None,
            "image_urls": None,
        }
        if app_id == TEXT
        else {"image_url": URL, "mode": "default"}
    )
    assert result.model_dump() == {"app_id": app_id, **expected}
    assert result.random_seed_field == ("seed" if app_id == TEXT else None)
    assert config_class_for_app_id(app_id) is type(result)
    assert TypeAdapter(FalConfig).validate_python(result.model_dump()) == result
    with pytest.raises(ValidationError, match="prompt" if app_id == TEXT else "image_url"):
        validate_parameters(app_id, {})


@pytest.mark.parametrize(
    ("field", "values"),
    [
        ("prompt", ["x", "x" * 9500]),
        ("quality", ["low", "medium", "high"]),
        ("num_images", [1, 8]),
        ("seed", [None, 0, 2147483647]),
        ("image_urls", [None, [], [URL] * 5]),
        (
            "aspect_ratio",
            [
                "auto",
                "1:1",
                "1:4",
                "1:3",
                "1:2",
                "9:16",
                "10:16",
                "2:3",
                "3:4",
                "4:5",
                "5:4",
                "4:3",
                "3:2",
                "16:10",
                "16:9",
                "2:1",
                "3:1",
                "4:1",
            ],
        ),
    ],
)
def test_text_to_vector_accepts_enums_and_boundaries(field: str, values: list[object]) -> None:
    for value in values:
        assert config(TEXT, **{field: value}).model_dump()[field] == value


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", ""),
        ("prompt", "x" * 9501),
        ("prompt", None),
        ("quality", "very_low"),
        ("num_images", 0),
        ("num_images", 9),
        ("seed", -1),
        ("seed", 2147483648),
        ("image_urls", [URL] * 6),
        ("aspect_ratio", "5:1"),
        ("mode", "simple"),
    ],
)
def test_text_to_vector_rejects_invalid_fields(field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        config(TEXT, **{field: value})


def test_image_to_vector_accepts_modes_and_rejects_unsupported_fields() -> None:
    for mode in ["default", "simple"]:
        assert config(IMAGE, mode=mode).mode == mode
    for field, value in [("mode", "complex"), ("image_url", None), ("seed", 1), ("prompt", "x")]:
        with pytest.raises(ValidationError, match=field):
            config(IMAGE, **{field: value})


def test_vector_cli_lists_models_and_emits_valid_examples() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert {TEXT, IMAGE} <= set(result.stdout.splitlines())
    for app_id in [TEXT, IMAGE]:
        result = runner.invoke(app, ["schema", app_id])
        assert result.exit_code == 0
        payload = YAML(typ="safe").load(result.stdout)
        assert payload["app_id"] == app_id
        assert validate_parameters(app_id, payload["parameters"]) is not None

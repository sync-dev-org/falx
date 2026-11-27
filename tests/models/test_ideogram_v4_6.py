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

APP_IDS = ("ideogram/v4.6", "ideogram/v4.6/edit")
EDIT = APP_IDS[1]
IMAGE = "https://example.com/image.png"
BOX = {"x_min": 0, "y_min": 0, "x_max": 256, "y_max": 256}


def parameters(app_id: str) -> dict[str, object]:
    result: dict[str, object] = {"prompt": "A colorful storefront."}
    if app_id == EDIT:
        result["image_url"] = IMAGE
    return result


def config(app_id: str, **values: object):
    assert app_id in SUPPORTED_APP_IDS
    result = validate_parameters(app_id, {**parameters(app_id), **values})
    assert result is not None
    return result


@pytest.mark.parametrize("app_id", APP_IDS)
def test_v46_registers_and_preserves_defaults(app_id: str) -> None:
    result = config(app_id)
    expected = {
        "app_id": app_id,
        **parameters(app_id),
        "image_size": "auto",
        "quality": "medium",
        "background": None,
        "num_images": 1,
        "seed": None,
        "sync_mode": False,
        "enable_safety_checker": True,
    }
    if app_id == EDIT:
        expected.update(
            reference_image_urls=None,
            mask_url=None,
            edit_precision="regular",
            context_window="none",
            context_window_box=None,
        )
    else:
        expected["enable_prompt_expansion"] = True
    assert result.model_dump() == expected
    assert result.random_seed_field == "seed"
    assert config_class_for_app_id(app_id) is type(result)
    assert TypeAdapter(FalConfig).validate_python(result.model_dump()) == result


@pytest.mark.parametrize("app_id", APP_IDS)
def test_v46_requires_prompt_and_edit_source(app_id: str) -> None:
    config(app_id)
    for field in parameters(app_id):
        with pytest.raises(ValidationError, match=field):
            validate_parameters(app_id, {k: v for k, v in parameters(app_id).items() if k != field})


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", ""),
        ("prompt", "x" * 10001),
        ("prompt", None),
        ("quality", "ultra"),
        ("background", "white"),
        ("num_images", 0),
        ("num_images", 9),
        ("image_size", "cinema"),
        ("image_size", {"width": 0}),
        ("image_size", {"height": 0}),
        ("image_size", {"width": 14143}),
        ("image_size", {"height": 14143}),
        ("image_size", {"width": 512, "extra": 1}),
        ("sync_mode", None),
        ("enable_safety_checker", None),
        ("output_format", "png"),
    ],
)
def test_v46_rejects_invalid_fields(app_id: str, field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        config(app_id, **{field: value})


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "values"),
    [
        ("prompt", ["x", "x" * 10000]),
        ("quality", ["very_low", "low", "medium", "high"]),
        ("background", [None, "transparent", "opaque"]),
        ("num_images", [1, 8]),
        ("seed", [None, -1, 2147483648]),
        ("sync_mode", [False, True]),
        ("enable_safety_checker", [False, True]),
        (
            "image_size",
            [
                "auto",
                "square",
                "square_hd",
                "portrait_4_3",
                "portrait_16_9",
                "landscape_4_3",
                "landscape_16_9",
                {},
                {"width": 1, "height": 14142},
                {"width": 14142, "height": 1},
                {"width": 257, "height": 4128},
            ],
        ),
    ],
)
def test_v46_accepts_enums_and_boundaries(app_id: str, field: str, values: list[object]) -> None:
    for value in values:
        result = config(app_id, **{field: value}).model_dump()[field]
        assert result == ({"width": 512, "height": 512} if value == {} else value)


@pytest.mark.parametrize("app_id", APP_IDS)
def test_v46_preserves_explicit_dimensions_for_each_quality(app_id: str) -> None:
    for quality in ["very_low", "low", "medium", "high"]:
        result = config(app_id, quality=quality, image_size={"width": 14142, "height": 14142})
        assert result.model_dump()["image_size"] == {"width": 14142, "height": 14142}


@pytest.mark.parametrize(
    "values",
    [
        {"reference_image_urls": [IMAGE] * 5},
        {"reference_image_urls": [IMAGE] * 4, "mask_url": IMAGE},
        {"edit_precision": "precise"},
        {"context_window": "full"},
        {"context_window": "auto"},
        {"context_window": "auto", "mask_url": IMAGE, "context_window_box": BOX},
        {"image_size": "square", "mask_url": IMAGE},
        {"image_size": {"width": 512}, "edit_precision": "high"},
        {"edit_precision": "high", "background": "transparent"},
        {"image_url": None},
        {"enable_prompt_expansion": True},
        {"context_window_box": {"x_min": 0}},
        {"context_window_box": {**BOX, "x_min": -1}},
    ],
)
def test_v46_edit_rejects_invalid_edit_combinations(values: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        config(EDIT, **values)


def test_v46_edit_accepts_masked_and_localized_edits() -> None:
    result = config(
        EDIT,
        edit_precision="high",
        mask_url=IMAGE,
        context_window="auto",
        reference_image_urls=[IMAGE] * 3,
    )
    assert result.context_window == "auto"
    assert result.reference_image_urls == [IMAGE] * 3
    for box in [
        BOX,
        {"x_min": 10, "y_min": 20, "x_max": 1546, "y_max": 276},
        {"x_min": 0, "y_min": 0, "x_max": 2048, "y_max": 2048},
        {"x_min": 0, "y_min": 0, "x_max": 1, "y_max": 20000},
        {"x_min": 0, "y_min": 0, "x_max": 20000, "y_max": 20000},
    ]:
        assert (
            config(EDIT, edit_precision="high", context_window_box=box).model_dump()[
                "context_window_box"
            ]
            == box
        )
    assert config(EDIT, reference_image_urls=[IMAGE] * 4).reference_image_urls == [IMAGE] * 4
    assert config(EDIT, reference_image_urls=[]).reference_image_urls == []
    assert config(APP_IDS[0], enable_prompt_expansion=False).enable_prompt_expansion is False


def test_v46_cli_lists_models_and_emits_valid_examples() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())
    for app_id in APP_IDS:
        result = runner.invoke(app, ["schema", app_id])
        assert result.exit_code == 0
        payload = YAML(typ="safe").load(result.stdout)
        assert payload["app_id"] == app_id
        assert validate_parameters(app_id, payload["parameters"]) is not None

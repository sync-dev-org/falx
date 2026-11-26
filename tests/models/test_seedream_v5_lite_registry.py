from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    SeedreamV5LiteEditConfig,
    SeedreamV5LiteTextToImageConfig,
    config_class_for_app_id,
    validate_parameters,
)

APP_IDS = (
    "bytedance/seedream/v5/lite/text-to-image",
    "bytedance/seedream/v5/lite/edit",
    "fal-ai/bytedance/seedream/v5/lite/text-to-image",
    "fal-ai/bytedance/seedream/v5/lite/edit",
)


def _parameters(app_id: str) -> dict[str, object]:
    parameters: dict[str, object] = {"prompt": "A ceramic vase."}
    if app_id.endswith("/edit"):
        parameters["image_urls"] = []
    return parameters


@pytest.mark.parametrize("app_id", APP_IDS)
def test_seedream_lite_ids_share_configs_and_current_defaults(app_id: str) -> None:
    expected_class = (
        SeedreamV5LiteEditConfig if app_id.endswith("/edit") else SeedreamV5LiteTextToImageConfig
    )
    config = TypeAdapter(FalConfig).validate_python({"app_id": app_id, **_parameters(app_id)})

    assert config_class_for_app_id(app_id) is expected_class
    assert isinstance(config, expected_class)
    assert config.random_seed_field is None
    expected = {
        "app_id": app_id,
        **_parameters(app_id),
        "image_size": "auto_2K",
        "num_images": 1,
        "max_images": 1,
        "sync_mode": False,
        "enable_safety_checker": True,
        "output_format": "jpeg",
        "watermark": False,
        "sequential_image_generation": None,
    }
    if app_id.endswith("/text-to-image"):
        expected["return_byteplus_urls"] = False
    assert config.model_dump() == expected


def test_models_lists_both_seedream_lite_id_prefixes() -> None:
    result = CliRunner().invoke(app, ["models"])

    assert result.exit_code == 0
    assert set(APP_IDS) <= SUPPORTED_APP_IDS
    assert set(APP_IDS) <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", APP_IDS)
def test_schema_prints_current_seedream_lite_job_example(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    job = YAML(typ="safe").load(result.stdout)
    assert job["app_id"] == app_id
    assert job["parameters"]["output_format"] == "jpeg"
    assert job["parameters"]["watermark"] is False
    assert job["parameters"]["sequential_image_generation"] is None
    assert validate_parameters(app_id, job["parameters"]) is not None


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("sequential_image_generation", ("auto", "disabled", None))
def test_seedream_lite_accepts_current_generation_options_and_boundaries(
    app_id: str, sequential_image_generation: str | None
) -> None:
    parameters = {
        **_parameters(app_id),
        "max_images": 15,
        "output_format": "png",
        "watermark": True,
        "sequential_image_generation": sequential_image_generation,
        "image_size": {"width": 1, "height": 16384},
    }
    config = validate_parameters(app_id, parameters)

    assert config is not None
    for field, expected in parameters.items():
        assert config.model_dump()[field] == expected


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("max_images", 0),
        ("max_images", 16),
        ("num_images", 0),
        ("num_images", 7),
        ("output_format", "webp"),
        ("sequential_image_generation", "always"),
        ("image_size", {"width": 16385, "height": 1024}),
        ("image_size", {"width": 1024, "height": 16385}),
        ("image_size", {"width": 0, "height": 1024}),
        ("image_size", {"width": 1024, "height": 0}),
    ],
)
def test_seedream_lite_rejects_values_outside_current_schema(
    app_id: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**_parameters(app_id), field: value})


@pytest.mark.parametrize("app_id", APP_IDS)
def test_seedream_lite_rejects_missing_prompt(app_id: str) -> None:
    parameters = _parameters(app_id)
    parameters.pop("prompt")

    with pytest.raises(ValidationError, match="prompt"):
        validate_parameters(app_id, parameters)


@pytest.mark.parametrize("app_id", (APP_IDS[1], APP_IDS[3]))
def test_seedream_lite_edits_require_image_urls(app_id: str) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        validate_parameters(app_id, {"prompt": "Edit the vase."})

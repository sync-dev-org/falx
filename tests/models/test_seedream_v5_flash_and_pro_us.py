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

FLASH_TEXT = "bytedance/seedream/v5/flash/text-to-image"
FLASH_EDIT = "bytedance/seedream/v5/flash/edit"
FLASH_LAYERIZE = "bytedance/seedream/v5/flash/layerize"
PRO_US_TEXT = "bytedance/seedream/v5/pro/us/text-to-image"
PRO_US_EDIT = "bytedance/seedream/v5/pro/us/edit"
GENERATION_APP_IDS = (FLASH_TEXT, FLASH_EDIT, PRO_US_TEXT, PRO_US_EDIT)
APP_IDS = (*GENERATION_APP_IDS, FLASH_LAYERIZE)
PRESETS = (
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
    "auto_1K",
    "auto_1.5K",
    "auto_2K",
)


def _parameters(app_id: str) -> dict[str, object]:
    if app_id == FLASH_LAYERIZE:
        return {"image_url": "https://example.com/input.png"}
    parameters: dict[str, object] = {"prompt": "A ceramic vase."}
    if app_id.endswith("/edit"):
        parameters["image_urls"] = ["https://example.com/input.png"]
    return parameters


def _defaults(app_id: str) -> dict[str, object]:
    defaults: dict[str, object] = {
        "image_size": "auto_2K",
        "num_images": 1,
        "output_format": "jpeg",
        "watermark": False,
        "sync_mode": False,
        "enable_safety_checker": True,
    }
    if app_id == FLASH_LAYERIZE:
        defaults.update(prompt="", image_size="auto", output_format="png")
        defaults.pop("num_images")
    if app_id.endswith("/edit"):
        defaults["background"] = "opaque"
    if "/pro/us/" in app_id:
        defaults["enhance_prompt_mode"] = "standard"
    return defaults


@pytest.mark.parametrize("app_id", APP_IDS)
def test_seedream_flash_and_pro_us_validate_defaults_and_discriminator(app_id: str) -> None:
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    config = TypeAdapter(FalConfig).validate_python({"app_id": app_id, **_parameters(app_id)})

    assert isinstance(config, config_class)
    assert config.random_seed_field is None
    assert config.model_dump() == {"app_id": app_id, **_defaults(app_id), **_parameters(app_id)}


def test_models_lists_seedream_flash_and_pro_us() -> None:
    result = CliRunner().invoke(app, ["models"])

    assert result.exit_code == 0
    assert set(APP_IDS) <= SUPPORTED_APP_IDS
    assert set(APP_IDS) <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", APP_IDS)
def test_schema_prints_valid_seedream_flash_and_pro_us_job_examples(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    job = YAML(typ="safe").load(result.stdout)
    expected_parameters = {**_defaults(app_id), **_parameters(app_id)}
    if "prompt" in expected_parameters and app_id != FLASH_LAYERIZE:
        expected_parameters["prompt"] = "<your prompt here>"
    if "image_urls" in expected_parameters:
        expected_parameters["image_urls"] = ["https://example.com/input"]
    if "image_url" in expected_parameters:
        expected_parameters["image_url"] = "https://example.com/input"
    assert job["app_id"] == app_id
    assert job["parameters"] == expected_parameters
    assert validate_parameters(app_id, job["parameters"]) is not None


@pytest.mark.parametrize("app_id", GENERATION_APP_IDS)
@pytest.mark.parametrize("image_size", PRESETS)
def test_seedream_flash_and_pro_us_accept_size_presets(app_id: str, image_size: str) -> None:
    config = validate_parameters(app_id, {**_parameters(app_id), "image_size": image_size})

    assert config is not None
    assert config.model_dump()["image_size"] == image_size


@pytest.mark.parametrize("app_id", GENERATION_APP_IDS)
def test_seedream_flash_and_pro_us_accept_generation_boundaries_and_options(app_id: str) -> None:
    parameters = {
        **_parameters(app_id),
        "image_size": {"width": 1, "height": 14142},
        "num_images": 6,
        "output_format": "png",
        "watermark": True,
        "sync_mode": True,
        "enable_safety_checker": False,
    }
    if app_id.endswith("/edit"):
        parameters["background"] = "transparent"
    if "/pro/us/" in app_id:
        parameters["enhance_prompt_mode"] = "fast"
    config = validate_parameters(app_id, parameters)

    assert config is not None
    assert config.model_dump() == {"app_id": app_id, **_defaults(app_id), **parameters}


@pytest.mark.parametrize("app_id", GENERATION_APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("num_images", 0),
        ("num_images", 7),
        ("image_size", "auto_3K"),
        ("image_size", {"width": 0, "height": 1024}),
        ("image_size", {"width": 1024, "height": 0}),
        ("image_size", {"width": 14143, "height": 1024}),
        ("image_size", {"width": 1024, "height": 14143}),
        ("output_format", "webp"),
    ],
)
def test_seedream_flash_and_pro_us_reject_invalid_generation_options(
    app_id: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**_parameters(app_id), field: value})


@pytest.mark.parametrize("app_id", (FLASH_EDIT, PRO_US_EDIT))
@pytest.mark.parametrize("count", (0, 11))
def test_seedream_flash_and_pro_us_edits_preserve_reference_array_shape(
    app_id: str, count: int
) -> None:
    references = [f"https://example.com/{index}.png" for index in range(count)]
    config = validate_parameters(app_id, {**_parameters(app_id), "image_urls": references})

    assert config is not None
    assert config.model_dump()["image_urls"] == references


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("field", ("seed", "unexpected"))
def test_seedream_flash_and_pro_us_reject_unsupported_fields(app_id: str, field: str) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**_parameters(app_id), field: 42})


@pytest.mark.parametrize(
    ("app_id", "field"),
    [(app_id, "prompt") for app_id in GENERATION_APP_IDS]
    + [(FLASH_EDIT, "image_urls"), (PRO_US_EDIT, "image_urls"), (FLASH_LAYERIZE, "image_url")],
)
def test_seedream_flash_and_pro_us_reject_missing_required_inputs(app_id: str, field: str) -> None:
    parameters = _parameters(app_id)
    parameters.pop(field)

    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, parameters)


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [
        (FLASH_TEXT, "background", "opaque"),
        (FLASH_TEXT, "enhance_prompt_mode", "fast"),
        (FLASH_EDIT, "enhance_prompt_mode", "fast"),
        (FLASH_EDIT, "background", "auto"),
        (PRO_US_TEXT, "background", "opaque"),
        (PRO_US_TEXT, "enhance_prompt_mode", "invalid"),
        (PRO_US_EDIT, "enhance_prompt_mode", "invalid"),
        (PRO_US_EDIT, "background", "auto"),
        (FLASH_LAYERIZE, "image_size", "auto_3K"),
        (FLASH_LAYERIZE, "enhance_prompt_mode", "fast"),
        (FLASH_LAYERIZE, "output_format", "webp"),
        (FLASH_LAYERIZE, "num_images", 1),
    ],
)
def test_seedream_flash_and_pro_us_reject_options_not_supported_by_endpoint(
    app_id: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**_parameters(app_id), field: value})


@pytest.mark.parametrize("image_size", ("auto", "auto_1K", "auto_1.5K", "auto_2K"))
@pytest.mark.parametrize("output_format", ("jpeg", "png"))
def test_seedream_flash_layerize_accepts_resolution_and_base_image_format(
    image_size: str, output_format: str
) -> None:
    parameters = {
        "image_url": "https://example.com/input.png",
        "prompt": "Separate the vase.",
        "image_size": image_size,
        "output_format": output_format,
        "watermark": True,
        "sync_mode": True,
        "enable_safety_checker": False,
    }
    config = validate_parameters(FLASH_LAYERIZE, parameters)

    assert config is not None
    assert config.model_dump() == {"app_id": FLASH_LAYERIZE, **parameters}

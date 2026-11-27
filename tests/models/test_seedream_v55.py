from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

import falx.models as models
from falx.cli import app
from falx.models import SUPPORTED_APP_IDS, config_class_for_app_id, validate_parameters

TEXT = "bytedance/seedream/v5.5/text-to-image"
EDIT = "bytedance/seedream/v5.5/edit"
LAYERIZE = "bytedance/seedream/v5.5/layerize"
GENERATORS = (TEXT, EDIT)
APP_IDS = (*GENERATORS, LAYERIZE)
IMAGE_URL = "https://example.com/input.png"


def _parameters(app_id: str) -> dict[str, object]:
    if app_id == LAYERIZE:
        return {"image_url": IMAGE_URL}
    parameters: dict[str, object] = {"prompt": "A ceramic vase."}
    if app_id == EDIT:
        parameters["image_urls"] = [IMAGE_URL]
    return parameters


@pytest.mark.parametrize(
    ("app_id", "class_name"),
    [
        (TEXT, "SeedreamV55TextToImageConfig"),
        (EDIT, "SeedreamV55EditConfig"),
        (LAYERIZE, "SeedreamV55LayerizeConfig"),
    ],
)
def test_registered_endpoints_validate_with_exported_configs(app_id: str, class_name: str) -> None:
    """Each endpoint routes parameters to its exported configuration class without a seed."""
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    assert config_class is getattr(models, class_name)
    assert config_class.random_seed_field is None
    config = validate_parameters(app_id, _parameters(app_id))
    assert isinstance(config, config_class)


@pytest.mark.parametrize("app_id", GENERATORS)
def test_generation_defaults_match_api(app_id: str) -> None:
    """Generation uses PNG, automatic background, and the documented optional defaults."""
    config = validate_parameters(app_id, _parameters(app_id))
    assert config is not None
    assert config.model_dump() == {
        "app_id": app_id,
        **_parameters(app_id),
        "image_size": "auto_2K",
        "num_images": 1,
        "output_format": "png",
        "background": "auto",
        "watermark": False,
        "sync_mode": False,
        "enable_safety_checker": True,
    }


def test_layerize_defaults_match_api() -> None:
    """Layerize permits an omitted prompt and defaults to 30 output images with OCR disabled."""
    config = validate_parameters(LAYERIZE, _parameters(LAYERIZE))
    assert config is not None
    assert config.model_dump() == {
        "app_id": LAYERIZE,
        "image_url": IMAGE_URL,
        "prompt": "",
        "image_size": "auto",
        "max_images": 30,
        "enable_text_recognition": False,
        "output_format": "png",
        "watermark": False,
        "sync_mode": False,
        "enable_safety_checker": True,
    }


@pytest.mark.parametrize("app_id", APP_IDS)
def test_optional_settings_are_preserved_in_request(app_id: str) -> None:
    """Explicit options survive validation, including OCR and layer counts above 30 in sync mode."""
    parameters = {
        **_parameters(app_id),
        "prompt": "Separate the vase.",
        "image_size": "auto_1.5K",
        "output_format": "jpeg",
        "watermark": True,
        "sync_mode": True,
        "enable_safety_checker": False,
    }
    if app_id == LAYERIZE:
        parameters.update(max_images=100, enable_text_recognition=True)
    else:
        parameters.update(num_images=6, background="opaque")
    config = validate_parameters(app_id, parameters)
    assert config is not None
    assert config.model_dump(exclude={"app_id"}) == parameters


@pytest.mark.parametrize("app_id", GENERATORS)
@pytest.mark.parametrize(
    "image_size",
    [
        "square_hd",
        "square",
        "portrait_4_3",
        "portrait_16_9",
        "landscape_4_3",
        "landscape_16_9",
        "auto_1K",
        "auto_1.5K",
        "auto_2K",
    ],
)
def test_generation_accepts_image_size_presets(app_id: str, image_size: str) -> None:
    """Generation accepts each documented resolution preset."""
    config = validate_parameters(app_id, {**_parameters(app_id), "image_size": image_size})
    assert config is not None
    assert config.model_dump()["image_size"] == image_size


@pytest.mark.parametrize("image_size", ["auto", "auto_1K", "auto_1.5K", "auto_2K"])
def test_layerize_accepts_resolution_tiers(image_size: str) -> None:
    """Layerize accepts its four resolution tiers."""
    config = validate_parameters(LAYERIZE, {**_parameters(LAYERIZE), "image_size": image_size})
    assert config is not None
    assert config.model_dump()["image_size"] == image_size


@pytest.mark.parametrize("app_id", GENERATORS)
@pytest.mark.parametrize("background", ["auto", "opaque", "transparent"])
def test_generation_accepts_background_modes_with_png(app_id: str, background: str) -> None:
    """PNG supports every background mode, including transparent output."""
    config = validate_parameters(app_id, {**_parameters(app_id), "background": background})
    assert config is not None
    assert config.model_dump()["background"] == background


@pytest.mark.parametrize("app_id", GENERATORS)
@pytest.mark.parametrize("num_images", [1, 6])
def test_generation_accepts_image_count_boundaries(app_id: str, num_images: int) -> None:
    """Generation accepts the minimum and maximum numbers of separate generations."""
    config = validate_parameters(app_id, {**_parameters(app_id), "num_images": num_images})
    assert config is not None
    assert config.model_dump()["num_images"] == num_images


@pytest.mark.parametrize("max_images", [2, 100])
def test_layerize_accepts_image_count_boundaries(max_images: int) -> None:
    """Layerize accepts between two and one hundred output images."""
    config = validate_parameters(LAYERIZE, {**_parameters(LAYERIZE), "max_images": max_images})
    assert config is not None
    assert config.model_dump()["max_images"] == max_images


@pytest.mark.parametrize("image_urls", [[], [IMAGE_URL] * 11])
def test_edit_passes_reference_images_without_a_local_count_limit(image_urls: list[str]) -> None:
    """The provider handles excess references; the input schema has no minimum reference count."""
    config = validate_parameters(EDIT, {"prompt": "Edit the vase.", "image_urls": image_urls})
    assert config is not None
    assert config.model_dump()["image_urls"] == image_urls


@pytest.mark.parametrize("app_id", GENERATORS)
@pytest.mark.parametrize(
    "image_size",
    [
        {"width": 1, "height": 1},
        {"width": 14142, "height": 14142},
        {"width": 5000, "height": 200},
        {"width": 200, "height": 5000},
    ],
)
def test_generation_accepts_custom_sizes_with_structured_dimension_bounds(
    app_id: str, image_size: dict[str, int]
) -> None:
    """Dimensions within explicit bounds pass even outside descriptive pixel and aspect limits."""
    config = validate_parameters(app_id, {**_parameters(app_id), "image_size": image_size})
    assert config is not None
    assert config.model_dump()["image_size"] == image_size


@pytest.mark.parametrize("app_id", GENERATORS)
def test_custom_size_uses_documented_dimension_defaults(app_id: str) -> None:
    """An omitted custom dimension defaults to 512 when the resulting size is supported."""
    config = validate_parameters(app_id, {**_parameters(app_id), "image_size": {"width": 2048}})
    assert config is not None
    assert config.model_dump()["image_size"] == {"width": 2048, "height": 512}


@pytest.mark.parametrize("app_id", GENERATORS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("num_images", 0),
        ("num_images", 7),
        ("background", "white"),
        ("image_size", "auto_3K"),
        ("image_size", {"width": 0, "height": 1024}),
        ("image_size", {"width": 1024, "height": 14143}),
        ("image_size", {"width": 1024, "height": 1024, "depth": 1}),
    ],
)
def test_generation_rejects_unsupported_counts_backgrounds_and_sizes(
    app_id: str, field: str, value: object
) -> None:
    """Invalid enums, counts, explicit dimension bounds, and unknown size fields are rejected."""
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**_parameters(app_id), field: value})


@pytest.mark.parametrize("app_id", GENERATORS)
def test_transparent_generation_requires_png(app_id: str) -> None:
    """A transparent background cannot be requested with JPEG output."""
    with pytest.raises(ValidationError, match="png"):
        validate_parameters(
            app_id,
            {**_parameters(app_id), "background": "transparent", "output_format": "jpeg"},
        )


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("field", ["output_format", "seed", "enhance_prompt_mode"])
def test_endpoints_reject_unsupported_format_and_parameters(app_id: str, field: str) -> None:
    """Unsupported output formats and options absent from this version's schema are rejected."""
    value = {"output_format": "webp", "seed": 123, "enhance_prompt_mode": "fast"}[field]
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**_parameters(app_id), field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [("max_images", 1), ("max_images", 101), ("image_size", "square"), ("image_url", None)],
)
def test_layerize_rejects_invalid_counts_tiers_and_input(field: str, value: object) -> None:
    """Layerize rejects unsupported layer counts, resolution tiers, and a null input URL."""
    with pytest.raises(ValidationError, match=field):
        validate_parameters(LAYERIZE, {**_parameters(LAYERIZE), field: value})


@pytest.mark.parametrize(
    ("app_id", "field"),
    [(TEXT, "prompt"), (EDIT, "prompt"), (EDIT, "image_urls"), (LAYERIZE, "image_url")],
)
def test_required_parameters_cannot_be_omitted(app_id: str, field: str) -> None:
    """Each required input must be supplied before a request can be submitted."""
    parameters = _parameters(app_id)
    del parameters[field]
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, parameters)


def test_models_command_lists_all_endpoints() -> None:
    """The model listing includes all three endpoints."""
    result = CliRunner().invoke(app, ["models"])
    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", APP_IDS)
def test_schema_examples_validate_for_each_endpoint(app_id: str) -> None:
    """CLI examples use API defaults and satisfy their endpoint's validation rules."""
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    config = validate_parameters(app_id, payload["parameters"])
    assert config is not None
    assert config.model_dump(exclude={"app_id"}) == payload["parameters"]
    assert payload["parameters"]["output_format"] == "png"
    if app_id == LAYERIZE:
        assert payload["parameters"]["max_images"] == 30
        assert payload["parameters"]["enable_text_recognition"] is False
    else:
        assert payload["parameters"]["background"] == "auto"

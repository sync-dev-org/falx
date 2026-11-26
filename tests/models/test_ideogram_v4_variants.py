from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    BaseFalConfig,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

APP_IDS = (
    "ideogram/v4/fast",
    "ideogram/v4/instant",
    "ideogram/v4/lora",
    "ideogram/v4/image-to-image",
    "ideogram/v4/image-to-image/lora",
    "ideogram/v4/tiling",
    "ideogram/v4/tiling/lora",
)
LORA_APP_IDS = tuple(app_id for app_id in APP_IDS if app_id.endswith("/lora"))
IMAGE_APP_IDS = tuple(app_id for app_id in APP_IDS if "/image-to-image" in app_id)
TILING_APP_IDS = tuple(app_id for app_id in APP_IDS if "/tiling" in app_id)
runner = CliRunner()
safe_yaml = YAML(typ="safe")


def required_parameters(app_id: str) -> dict[str, object]:
    parameters: dict[str, object] = {"prompt": "A seamless botanical illustration."}
    if app_id in IMAGE_APP_IDS:
        parameters["image_url"] = "https://example.com/source.png"
    return parameters


def expected_parameters(app_id: str) -> dict[str, object]:
    parameters = {
        **required_parameters(app_id),
        "expansion_model": "Medium",
        "image_size": "auto" if app_id in IMAGE_APP_IDS else "square_hd",
        "num_images": 1,
        "seed": None,
        "sync_mode": False,
        "enable_safety_checker": True,
        "output_format": "jpeg",
    }
    if app_id != "ideogram/v4/instant":
        parameters["rendering_speed"] = "BALANCED"
    if app_id not in ("ideogram/v4/fast", "ideogram/v4/instant"):
        parameters["acceleration"] = "none"
    if app_id in IMAGE_APP_IDS or app_id in TILING_APP_IDS:
        parameters["strength"] = 0.8
    if app_id in TILING_APP_IDS:
        parameters.update(image_url=None, mask_url=None, tiling_mode="both")
    if app_id in LORA_APP_IDS:
        parameters["loras"] = []
    return parameters


def registered_config(app_id: str, **parameters: object) -> BaseFalConfig:
    assert app_id in SUPPORTED_APP_IDS
    config = validate_parameters(app_id, {**required_parameters(app_id), **parameters})
    assert config is not None
    return config


@pytest.mark.parametrize("app_id", APP_IDS)
def test_ideogram_variants_register_route_and_preserve_openapi_defaults(app_id: str) -> None:
    config = registered_config(app_id)

    assert config_class_for_app_id(app_id) is type(config)
    assert TypeAdapter(FalConfig).validate_python(config.model_dump()) == config
    assert config.random_seed_field == "seed"
    assert config.model_dump() == {"app_id": app_id, **expected_parameters(app_id)}


@pytest.mark.parametrize("app_id", APP_IDS)
def test_ideogram_variants_require_prompt_and_source_image_when_applicable(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    with pytest.raises(ValidationError, match="prompt"):
        validate_parameters(
            app_id, {k: v for k, v in required_parameters(app_id).items() if k != "prompt"}
        )
    if app_id in IMAGE_APP_IDS:
        with pytest.raises(ValidationError, match="image_url"):
            validate_parameters(app_id, {"prompt": "A print."})


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", None),
        ("expansion_model", "Small"),
        ("image_size", "cinema"),
        ("num_images", 0),
        ("num_images", 5),
        ("output_format", "webp"),
        ("sync_mode", None),
        ("enable_safety_checker", None),
        ("unexpected", True),
    ],
)
def test_ideogram_variants_reject_invalid_parameters(
    app_id: str,
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError, match=field):
        registered_config(app_id, **{field: value})


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("num_images", [1, 4])
def test_ideogram_variants_accept_image_count_limits_and_nullable_seed(
    app_id: str,
    num_images: int,
) -> None:
    config = registered_config(app_id, num_images=num_images, seed=None, prompt="")

    assert config.num_images == num_images
    assert config.seed is None
    assert config.prompt == ""


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    "image_size",
    [
        "square_hd",
        "square",
        "portrait_4_3",
        "portrait_16_9",
        "landscape_4_3",
        "landscape_16_9",
        {"width": 1, "height": 14142},
    ],
)
def test_ideogram_variants_accept_presets_and_custom_image_size_limits(
    app_id: str,
    image_size: object,
) -> None:
    config = registered_config(app_id, image_size=image_size)

    assert config.model_dump()["image_size"] == image_size


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    "image_size", [{"width": 0}, {"height": 0}, {"width": 14143}, {"height": 14143}, {"unit": "px"}]
)
def test_ideogram_variants_reject_invalid_custom_image_sizes(
    app_id: str,
    image_size: object,
) -> None:
    with pytest.raises(ValidationError, match="image_size"):
        registered_config(app_id, image_size=image_size)


@pytest.mark.parametrize(
    ("app_id", "field", "values"),
    [(app_id, "expansion_model", ["None", "Medium"]) for app_id in APP_IDS]
    + [
        (app_id, "expansion_model", ["Large"])
        for app_id in APP_IDS
        if app_id not in ("ideogram/v4/fast", "ideogram/v4/instant")
    ]
    + [
        (app_id, "rendering_speed", ["TURBO", "BALANCED", "QUALITY"])
        for app_id in APP_IDS
        if app_id != "ideogram/v4/instant"
    ]
    + [
        (app_id, "acceleration", ["none", "low", "regular", "high"])
        for app_id in APP_IDS
        if app_id not in ("ideogram/v4/fast", "ideogram/v4/instant")
    ]
    + [(app_id, "output_format", ["jpeg", "png"]) for app_id in APP_IDS]
    + [(app_id, "tiling_mode", ["both", "horizontal", "vertical"]) for app_id in TILING_APP_IDS],
)
def test_ideogram_variants_accept_their_enum_values(
    app_id: str,
    field: str,
    values: list[str],
) -> None:
    for value in values:
        assert registered_config(app_id, **{field: value}).model_dump()[field] == value


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [(app_id, "expansion_model", "Large") for app_id in APP_IDS[:2]]
    + [(app_id, "acceleration", "none") for app_id in APP_IDS[:2]]
    + [("ideogram/v4/instant", "rendering_speed", "BALANCED")]
    + [(app_id, "rendering_speed", "FAST") for app_id in APP_IDS if app_id != "ideogram/v4/instant"]
    + [(app_id, "acceleration", "maximum") for app_id in APP_IDS[2:]]
    + [(app_id, "image_size", "auto") for app_id in APP_IDS if app_id not in IMAGE_APP_IDS]
    + [(app_id, "tiling_mode", "diagonal") for app_id in TILING_APP_IDS],
)
def test_ideogram_variants_reject_fields_and_enums_from_other_variants(
    app_id: str,
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError, match=field):
        registered_config(app_id, **{field: value})


@pytest.mark.parametrize("app_id", IMAGE_APP_IDS + TILING_APP_IDS)
@pytest.mark.parametrize("strength", [0, 1])
def test_ideogram_image_transforms_accept_strength_limits(app_id: str, strength: float) -> None:
    assert registered_config(app_id, strength=strength).strength == strength


@pytest.mark.parametrize("app_id", IMAGE_APP_IDS + TILING_APP_IDS)
@pytest.mark.parametrize("strength", [-0.1, 1.1])
def test_ideogram_image_transforms_reject_strength_outside_limits(
    app_id: str,
    strength: float,
) -> None:
    with pytest.raises(ValidationError, match="strength"):
        registered_config(app_id, strength=strength)


@pytest.mark.parametrize("app_id", IMAGE_APP_IDS)
def test_ideogram_image_transforms_reject_null_source_images(app_id: str) -> None:
    with pytest.raises(ValidationError, match="image_url"):
        registered_config(app_id, image_url=None)


@pytest.mark.parametrize("app_id", TILING_APP_IDS)
def test_ideogram_tiling_preserves_source_and_mask_for_inpainting(app_id: str) -> None:
    config = registered_config(
        app_id,
        image_url="https://example.com/texture.png",
        mask_url="https://example.com/mask.png",
        tiling_mode="horizontal",
        strength=0.4,
    )

    assert config.model_dump() == {
        "app_id": app_id,
        **expected_parameters(app_id),
        "image_url": "https://example.com/texture.png",
        "mask_url": "https://example.com/mask.png",
        "tiling_mode": "horizontal",
        "strength": 0.4,
    }


@pytest.mark.parametrize("app_id", LORA_APP_IDS)
def test_ideogram_lora_variants_accept_weights_and_preserve_nested_defaults(app_id: str) -> None:
    loras = [
        {"path": "https://example.com/style.safetensors"},
        {"path": "https://example.com/zero.safetensors", "scale": 0},
        {"path": "https://example.com/strong.safetensors", "scale": 4},
    ]
    config = registered_config(app_id, loras=loras)

    assert config.model_dump()["loras"] == [{**loras[0], "scale": 1.0}, *loras[1:]]
    assert registered_config(app_id).loras == []


@pytest.mark.parametrize("app_id", LORA_APP_IDS)
@pytest.mark.parametrize(
    "loras",
    [
        [{"path": "https://example.com/style.safetensors"}] * 4,
        [{"scale": 1}],
        [{"path": "https://example.com/style.safetensors", "scale": -0.1}],
        [{"path": "https://example.com/style.safetensors", "scale": 4.1}],
        [{"path": "https://example.com/style.safetensors", "unexpected": True}],
        None,
    ],
)
def test_ideogram_lora_variants_reject_invalid_weights(app_id: str, loras: object) -> None:
    with pytest.raises(ValidationError, match="loras"):
        registered_config(app_id, loras=loras)


def test_ideogram_models_command_lists_all_variants() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", APP_IDS)
def test_ideogram_schema_examples_contain_valid_required_inputs_and_defaults(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    job = safe_yaml.load(result.stdout)
    expected = {**expected_parameters(app_id), "prompt": "<your prompt here>"}
    if app_id in IMAGE_APP_IDS:
        expected["image_url"] = "https://example.com/input"
    assert job["app_id"] == app_id
    assert job["parameters"] == expected
    assert validate_parameters(app_id, job["parameters"]) is not None

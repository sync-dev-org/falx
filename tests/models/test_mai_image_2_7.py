from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    BaseFalConfig,
    config_class_for_app_id,
    validate_parameters,
)

TEXT_APP_IDS = [
    "microsoft/mai-image-2.7/text-to-image",
    "microsoft/mai-image-2.7/flash/text-to-image",
]
EDIT_APP_IDS = [
    "microsoft/mai-image-2.7/edit",
    "microsoft/mai-image-2.7/flash/edit",
]
APP_IDS = TEXT_APP_IDS + EDIT_APP_IDS
IMAGE_SIZE_PRESETS = [
    "square_hd",
    "portrait_4_3",
    "landscape_4_3",
    "portrait_3_2",
    "landscape_3_2",
    "portrait_16_9",
    "landscape_16_9",
]


def parameters_for(app_id: str) -> dict[str, object]:
    parameters: dict[str, object] = {"prompt": "A ceramic teapot beside a window."}
    if app_id in EDIT_APP_IDS:
        parameters["image_urls"] = ["https://example.com/source.png"]
    return parameters


def validate(app_id: str, parameters: dict[str, object]) -> BaseFalConfig:
    assert app_id in SUPPORTED_APP_IDS
    config = validate_parameters(app_id, parameters)
    assert config is not None
    return config


@pytest.mark.parametrize("app_id", APP_IDS)
def test_mai_image_2_7_registers_models_with_schema_defaults(app_id: str) -> None:
    parameters = parameters_for(app_id)
    config = validate(app_id, parameters)

    assert type(config) is config_class_for_app_id(app_id)
    assert config.random_seed_field is None
    assert config.model_dump() == {
        "app_id": app_id,
        **parameters,
        "background": "opaque",
        "image_size": None if app_id in EDIT_APP_IDS else "square_hd",
        "output_format": "png",
        "sync_mode": False,
        "resolution": "1K",
    }


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("prompt", ["x", "x" * 20_000], ids=["minimum", "maximum"])
def test_mai_image_2_7_accepts_prompt_length_boundaries(app_id: str, prompt: str) -> None:
    config = validate(app_id, {**parameters_for(app_id), "prompt": prompt})

    assert config.prompt == prompt


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("image_size", IMAGE_SIZE_PRESETS)
def test_mai_image_2_7_accepts_image_size_presets(app_id: str, image_size: str) -> None:
    config = validate(app_id, {**parameters_for(app_id), "image_size": image_size})

    assert config.image_size == image_size


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    "image_size",
    [
        {"width": 768, "height": 768},
        {"width": 2048, "height": 2048},
        {"width": 769, "height": 1025},
        {"width": 1, "height": 1},
        {"width": 14142, "height": 14142},
    ],
)
def test_mai_image_2_7_accepts_custom_sizes_without_rounding(
    app_id: str, image_size: dict[str, int]
) -> None:
    config = validate(app_id, {**parameters_for(app_id), "image_size": image_size})

    assert config.model_dump()["image_size"] == image_size


@pytest.mark.parametrize("app_id", APP_IDS)
def test_mai_image_2_7_preserves_custom_size_defaults(app_id: str) -> None:
    config = validate(app_id, {**parameters_for(app_id), "image_size": {}})

    assert config.model_dump()["image_size"] == {"width": 512, "height": 512}


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("output_format", ["jpeg", "png", "webp"])
@pytest.mark.parametrize("resolution", ["1K", "2K"])
def test_mai_image_2_7_accepts_output_options(
    app_id: str, output_format: str, resolution: str
) -> None:
    config = validate(
        app_id,
        {
            **parameters_for(app_id),
            "output_format": output_format,
            "resolution": resolution,
            "sync_mode": True,
        },
    )

    assert config.output_format == output_format
    assert config.resolution == resolution
    assert config.sync_mode is True


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("output_format", ["png", "webp"])
def test_mai_image_2_7_accepts_transparent_background_with_alpha_formats(
    app_id: str, output_format: str
) -> None:
    config = validate(
        app_id,
        {**parameters_for(app_id), "background": "transparent", "output_format": output_format},
    )

    assert config.background == "transparent"


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("overrides", "needle"),
    [
        ({"prompt": ""}, "prompt"),
        ({"prompt": "x" * 20_001}, "prompt"),
        ({"prompt": None}, "prompt"),
        ({"background": "auto"}, "background"),
        ({"output_format": "gif"}, "output_format"),
        ({"resolution": "4K"}, "resolution"),
        ({"sync_mode": "invalid"}, "sync_mode"),
        ({"seed": 123}, "seed"),
        ({"image_size": "square"}, "image_size"),
        ({"image_size": "auto"}, "image_size"),
        ({"image_size": {"width": 14143, "height": 768}}, "image_size"),
        ({"image_size": {"width": 768, "height": 14143}}, "image_size"),
        ({"image_size": {"width": 0, "height": 768}}, "image_size"),
        ({"image_size": {"width": 768, "height": 0}}, "image_size"),
        ({"image_size": {"width": 768, "height": 768, "unit": "px"}}, "image_size"),
        ({"background": "transparent", "output_format": "jpeg"}, "background"),
    ],
    ids=[
        "empty-prompt",
        "long-prompt",
        "null-prompt",
        "invalid-background",
        "invalid-format",
        "invalid-resolution",
        "invalid-sync-mode",
        "unknown-seed",
        "invalid-square-preset",
        "invalid-auto-preset",
        "wide-image",
        "tall-image",
        "zero-width",
        "zero-height",
        "unknown-size-field",
        "transparent-jpeg",
    ],
)
def test_mai_image_2_7_rejects_invalid_parameters(
    app_id: str, overrides: dict[str, object], needle: str
) -> None:
    with pytest.raises(ValidationError, match=needle):
        validate(app_id, {**parameters_for(app_id), **overrides})


@pytest.mark.parametrize("app_id", APP_IDS)
def test_mai_image_2_7_requires_prompt(app_id: str) -> None:
    parameters = parameters_for(app_id)
    del parameters["prompt"]

    with pytest.raises(ValidationError, match="prompt"):
        validate(app_id, parameters)


@pytest.mark.parametrize("app_id", TEXT_APP_IDS)
def test_mai_image_2_7_text_to_image_rejects_null_size(app_id: str) -> None:
    with pytest.raises(ValidationError, match="image_size"):
        validate(app_id, {**parameters_for(app_id), "image_size": None})


@pytest.mark.parametrize("app_id", EDIT_APP_IDS)
@pytest.mark.parametrize("image_count", [1, 5])
def test_mai_image_2_7_edit_accepts_reference_count_boundaries(
    app_id: str, image_count: int
) -> None:
    image_urls = [f"https://example.com/{index}.png" for index in range(image_count)]
    config = validate(
        app_id, {**parameters_for(app_id), "image_urls": image_urls, "image_size": None}
    )

    assert config.image_urls == image_urls
    assert config.image_size is None


@pytest.mark.parametrize("app_id", EDIT_APP_IDS)
@pytest.mark.parametrize("image_urls", [None, [], ["image.png"] * 6, [123]])
def test_mai_image_2_7_edit_rejects_invalid_reference_lists(
    app_id: str, image_urls: object
) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        validate(app_id, {**parameters_for(app_id), "image_urls": image_urls})


@pytest.mark.parametrize("app_id", EDIT_APP_IDS)
def test_mai_image_2_7_edit_requires_reference_images(app_id: str) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        validate(app_id, {"prompt": "Make the teapot bright blue."})


@pytest.mark.parametrize("app_id", APP_IDS)
def test_mai_image_2_7_cli_lists_models_and_prints_valid_schema_examples(app_id: str) -> None:
    runner = CliRunner()
    models = runner.invoke(app, ["models"])
    schema = runner.invoke(app, ["schema", app_id])

    assert models.exit_code == 0
    assert app_id in models.stdout
    assert schema.exit_code == 0
    payload = YAML(typ="safe").load(schema.stdout)
    config = validate(app_id, payload["parameters"])
    assert config.app_id == app_id

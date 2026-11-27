from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx import models
from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    BaseFalConfig,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

APP_IDS = {
    "minimax/h3-image/edit": "MinimaxH3ImageEditConfig",
    "minimax/h3-image/highspeed/edit": "MinimaxH3ImageHighspeedEditConfig",
    "minimax/h3-image/highspeed/text-to-image": "MinimaxH3ImageHighspeedTextToImageConfig",
    "minimax/h3-image/text-to-image": "MinimaxH3ImageTextToImageConfig",
}
STANDARD_APP_IDS = [app_id for app_id in APP_IDS if "/highspeed/" not in app_id]
PRESETS = [
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
]
PROMPT = "A quiet garden in the morning."
IMAGE_URL = "https://example.com/reference.png"


def required_parameters(app_id: str) -> dict[str, object]:
    parameters: dict[str, object] = {"prompt": PROMPT}
    if app_id.endswith("/edit"):
        parameters["image_urls"] = [IMAGE_URL]
    return parameters


@pytest.fixture(params=APP_IDS)
def app_id(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def config_class(app_id: str) -> type[BaseFalConfig]:
    cls = config_class_for_app_id(app_id)
    assert cls is not None
    assert getattr(models, APP_IDS[app_id]) is cls
    return cls


def test_minimax_h3_image_registers_and_routes_parameters(
    app_id: str, config_class: type[BaseFalConfig]
) -> None:
    assert app_id in SUPPORTED_APP_IDS
    assert config_class.random_seed_field is None
    config = TypeAdapter(FalConfig).validate_python(
        {"app_id": app_id, **required_parameters(app_id)}
    )
    assert isinstance(config, config_class)
    assert isinstance(validate_parameters(app_id, required_parameters(app_id)), config_class)


def test_minimax_h3_image_uses_endpoint_defaults(
    app_id: str, config_class: type[BaseFalConfig]
) -> None:
    expected = {
        "app_id": app_id,
        **required_parameters(app_id),
        "image_size": "auto" if app_id.endswith("/edit") else {"width": 2048, "height": 2048},
        "num_images": 1,
        "output_format": "png",
        "sync_mode": False,
    }
    if app_id.endswith("/text-to-image"):
        expected["enable_prompt_expansion"] = True
    if app_id in STANDARD_APP_IDS:
        expected["loras"] = None
    config = config_class.model_validate({"app_id": app_id, **required_parameters(app_id)})
    assert config.model_dump() == expected


def test_minimax_h3_image_accepts_all_options_and_upper_boundaries(
    app_id: str, config_class: type[BaseFalConfig]
) -> None:
    payload = {
        "app_id": app_id,
        "prompt": "x" * 32_000,
        "image_size": {"width": 5000, "height": 4000},
        "num_images": 10,
        "output_format": "jpg",
        "sync_mode": True,
    }
    if app_id.endswith("/edit"):
        payload["image_urls"] = [IMAGE_URL] * 16
    else:
        payload["enable_prompt_expansion"] = False
    if app_id in STANDARD_APP_IDS:
        payload["loras"] = [
            {"path": "owner/adapter", "weight_name": "weights.safetensors", "scale": scale}
            for scale in (0, 0.5, 1, 4)
        ]
    assert config_class.model_validate(payload).model_dump() == payload


@pytest.mark.parametrize("image_size", PRESETS)
def test_minimax_h3_image_accepts_size_presets(
    app_id: str, config_class: type[BaseFalConfig], image_size: str
) -> None:
    config = config_class.model_validate(
        {"app_id": app_id, **required_parameters(app_id), "image_size": image_size}
    )
    assert config.image_size == image_size


@pytest.mark.parametrize("output_format", ["jpeg", "png", "webp", "jpg"])
def test_minimax_h3_image_accepts_output_formats(
    app_id: str, config_class: type[BaseFalConfig], output_format: str
) -> None:
    config = config_class.model_validate(
        {"app_id": app_id, **required_parameters(app_id), "output_format": output_format}
    )
    assert config.output_format == output_format


@pytest.mark.parametrize(
    "image_size",
    [
        {"width": 1024, "height": 640},
        {"width": 3000, "height": 1000},
        {"width": 1000, "height": 3000},
        {"width": 1024, "height": 639},
        {"width": 5000, "height": 4001},
        {"width": 3001, "height": 1000},
        {"width": 1000, "height": 3001},
    ],
)
def test_minimax_h3_image_accepts_custom_dimensions_within_schema_limits(
    app_id: str, config_class: type[BaseFalConfig], image_size: dict[str, int]
) -> None:
    config = config_class.model_validate(
        {"app_id": app_id, **required_parameters(app_id), "image_size": image_size}
    )
    assert config.model_dump()["image_size"] == image_size


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", ""),
        ("prompt", "x" * 32_001),
        ("prompt", None),
        ("num_images", 0),
        ("num_images", 11),
        ("num_images", 1.5),
        ("output_format", "gif"),
        ("sync_mode", "invalid"),
        ("image_size", "panorama"),
        ("image_size", {"width": 0, "height": 1024}),
        ("image_size", {"width": 1024, "height": 14143}),
        ("seed", 42),
        ("enable_safety_checker", True),
    ],
)
def test_minimax_h3_image_rejects_invalid_parameters(
    app_id: str, config_class: type[BaseFalConfig], field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_class.model_validate({"app_id": app_id, **required_parameters(app_id), field: value})


def test_minimax_h3_image_requires_prompt(app_id: str, config_class: type[BaseFalConfig]) -> None:
    parameters = required_parameters(app_id)
    del parameters["prompt"]
    with pytest.raises(ValidationError, match="prompt"):
        config_class.model_validate({"app_id": app_id, **parameters})


def test_minimax_h3_image_keeps_text_and_edit_options_distinct(
    app_id: str, config_class: type[BaseFalConfig]
) -> None:
    parameters = required_parameters(app_id)
    if app_id.endswith("/edit"):
        for image_urls in (None, [], [IMAGE_URL] * 17):
            with pytest.raises(ValidationError, match="image_urls"):
                config_class.model_validate(
                    {"app_id": app_id, **parameters, "image_urls": image_urls}
                )
        with pytest.raises(ValidationError, match="image_urls"):
            config_class.model_validate({"app_id": app_id, "prompt": PROMPT})
        invalid = {"enable_prompt_expansion": True}
    else:
        invalid = {"image_size": "auto"}
        with pytest.raises(ValidationError, match="image_urls"):
            config_class.model_validate({"app_id": app_id, **parameters, "image_urls": [IMAGE_URL]})
    with pytest.raises(ValidationError):
        config_class.model_validate({"app_id": app_id, **parameters, **invalid})


@pytest.mark.parametrize("app_id", STANDARD_APP_IDS)
def test_minimax_h3_image_accepts_optional_loras_and_adapter_defaults(app_id: str) -> None:
    config = validate_parameters(
        app_id, {**required_parameters(app_id), "loras": [{"path": "owner/adapter"}]}
    )
    assert config is not None
    assert config.model_dump()["loras"] == [
        {"path": "owner/adapter", "weight_name": None, "scale": 1}
    ]
    for loras in (None, []):
        config = validate_parameters(app_id, {**required_parameters(app_id), "loras": loras})
        assert config is not None
        assert config.model_dump()["loras"] == loras


@pytest.mark.parametrize("app_id", STANDARD_APP_IDS)
@pytest.mark.parametrize(
    "loras",
    [
        [{}],
        [{"path": "owner/adapter", "scale": -0.1}],
        [{"path": "owner/adapter", "scale": 4.1}],
        [{"path": "owner/adapter"}] * 5,
    ],
)
def test_minimax_h3_image_rejects_invalid_loras(app_id: str, loras: list[dict]) -> None:
    with pytest.raises(ValidationError, match="loras"):
        validate_parameters(app_id, {**required_parameters(app_id), "loras": loras})


@pytest.mark.parametrize("app_id", [app_id for app_id in APP_IDS if "/highspeed/" in app_id])
def test_minimax_h3_image_highspeed_rejects_loras(app_id: str) -> None:
    with pytest.raises(ValidationError, match="loras"):
        validate_parameters(app_id, {**required_parameters(app_id), "loras": []})


def test_minimax_h3_image_schema_describes_required_fields_and_limits(
    app_id: str, config_class: type[BaseFalConfig]
) -> None:
    schema = config_class.model_json_schema()
    expected_required = {"app_id", "prompt"}
    if app_id.endswith("/edit"):
        expected_required.add("image_urls")
    assert set(schema["required"]) == expected_required
    properties = schema["properties"]
    assert properties["prompt"]["minLength"] == 1
    assert properties["prompt"]["maxLength"] == 32_000
    assert properties["num_images"]["minimum"] == 1
    assert properties["num_images"]["maximum"] == 10
    size = schema["$defs"]["MinimaxH3ImageSize"]
    for dimension in ("width", "height"):
        assert size["properties"][dimension]["default"] == 512
        assert size["properties"][dimension]["exclusiveMinimum"] == 0
        assert size["properties"][dimension]["maximum"] == 14142
    if app_id.endswith("/edit"):
        assert properties["image_urls"]["minItems"] == 1
        assert properties["image_urls"]["maxItems"] == 16
    if app_id in STANDARD_APP_IDS:
        assert properties["loras"]["default"] is None
        assert properties["loras"]["anyOf"][0]["maxItems"] == 4


def test_minimax_h3_image_cli_lists_models_and_prints_valid_examples() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())
    for app_id in APP_IDS:
        result = runner.invoke(app, ["schema", app_id])
        assert result.exit_code == 0
        payload = YAML(typ="safe").load(result.stdout)
        assert payload["app_id"] == app_id
        config = validate_parameters(app_id, payload["parameters"])
        assert config is not None

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

DEPTH_APP_IDS = ["speridlabs/iris-z", "speridlabs/iris-z/small"]
DEPTH_TO_IMAGE_APP_IDS = [f"{app_id}/depth-to-image" for app_id in DEPTH_APP_IDS]
TEXT_APP_IDS = [
    f"{app_id}/{mode}" for app_id in DEPTH_APP_IDS for mode in ("text-to-image", "text-to-rgbd")
]
APP_IDS = DEPTH_APP_IDS + DEPTH_TO_IMAGE_APP_IDS + TEXT_APP_IDS

DEPTH_PARAMETERS = {"image_url": "https://example.com/image.png"}
DEPTH_DEFAULTS = {
    **DEPTH_PARAMETERS,
    "resolution": "auto",
    "num_inference_steps": 4,
    "ensemble_size": 1,
    "seed": None,
    "enable_safety_checker": True,
}
GENERATION_DEFAULTS = {
    "num_inference_steps": 50,
    "guidance_scale": None,
    "seed": None,
    "output_format": "png",
    "enable_safety_checker": True,
}
DEPTH_TO_IMAGE_PARAMETERS = {"depth_image_url": "https://example.com/depth.png"}
DEPTH_TO_IMAGE_DEFAULTS = {
    **DEPTH_TO_IMAGE_PARAMETERS,
    "depth_format": "colorized",
    "prompt": "",
    "resolution": "1024",
    **GENERATION_DEFAULTS,
}
TEXT_PARAMETERS = {"prompt": "A lighthouse above the waves."}
TEXT_DEFAULTS = {**TEXT_PARAMETERS, "image_size": "square_hd", **GENERATION_DEFAULTS}
CASES = (
    [(app_id, DEPTH_PARAMETERS, DEPTH_DEFAULTS) for app_id in DEPTH_APP_IDS]
    + [
        (app_id, DEPTH_TO_IMAGE_PARAMETERS, DEPTH_TO_IMAGE_DEFAULTS)
        for app_id in DEPTH_TO_IMAGE_APP_IDS
    ]
    + [(app_id, TEXT_PARAMETERS, TEXT_DEFAULTS) for app_id in TEXT_APP_IDS]
)


@pytest.mark.parametrize(("app_id", "parameters", "expected"), CASES)
def test_iris_z_validates_required_input_and_preserves_defaults(
    app_id: str, parameters: dict[str, object], expected: dict[str, object]
) -> None:
    config = validate_parameters(app_id, parameters)

    assert isinstance(config, BaseFalConfig)
    assert config.model_dump() == {"app_id": app_id, **expected}
    parsed = TypeAdapter(FalConfig).validate_python({"app_id": app_id, **parameters})
    assert type(parsed) is type(config)
    assert config.random_seed_field == "seed"


@pytest.mark.parametrize("app_id", APP_IDS)
def test_iris_z_rejects_missing_required_input(app_id: str) -> None:
    with pytest.raises(ValidationError):
        validate_parameters(app_id, {})


@pytest.mark.parametrize(("app_id", "parameters", "expected"), CASES)
@pytest.mark.parametrize("seed", [None, -1, 0, 2**40])
def test_iris_z_accepts_unbounded_nullable_seeds(
    app_id: str, parameters: dict[str, object], expected: dict[str, object], seed: int | None
) -> None:
    config = validate_parameters(app_id, {**parameters, "seed": seed})

    assert isinstance(config, BaseFalConfig)
    assert config.seed == seed


@pytest.mark.parametrize("app_id", DEPTH_APP_IDS)
@pytest.mark.parametrize("resolution", ["auto", "512", "1024"])
def test_iris_z_depth_accepts_resolutions_and_sampling_boundaries(
    app_id: str, resolution: str
) -> None:
    config = validate_parameters(
        app_id,
        {
            **DEPTH_PARAMETERS,
            "resolution": resolution,
            "num_inference_steps": 16,
            "ensemble_size": 10,
            "enable_safety_checker": False,
        },
    )

    assert isinstance(config, BaseFalConfig)
    assert config.resolution == resolution
    assert config.num_inference_steps == 16
    assert config.ensemble_size == 10
    assert config.enable_safety_checker is False
    minimum = validate_parameters(
        app_id, {**DEPTH_PARAMETERS, "num_inference_steps": 1, "ensemble_size": 1}
    )
    assert isinstance(minimum, BaseFalConfig)
    assert minimum.num_inference_steps == minimum.ensemble_size == 1


@pytest.mark.parametrize("app_id", DEPTH_APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("resolution", "2048"),
        ("num_inference_steps", 0),
        ("num_inference_steps", 17),
        ("ensemble_size", 0),
        ("ensemble_size", 11),
        ("image_url", None),
        ("prompt", "unsupported"),
    ],
)
def test_iris_z_depth_rejects_invalid_parameters(app_id: str, field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**DEPTH_PARAMETERS, field: value})


GENERATION_CASES = CASES[len(DEPTH_APP_IDS) :]


@pytest.mark.parametrize(("app_id", "parameters", "expected"), GENERATION_CASES)
@pytest.mark.parametrize("guidance_scale", [None, 1, 20])
def test_iris_z_generation_accepts_sampling_prompt_and_guidance_boundaries(
    app_id: str,
    parameters: dict[str, object],
    expected: dict[str, object],
    guidance_scale: float | None,
) -> None:
    config = validate_parameters(
        app_id,
        {
            **parameters,
            "prompt": "x" * 4096,
            "num_inference_steps": 1,
            "guidance_scale": guidance_scale,
            "output_format": "jpeg",
            "enable_safety_checker": False,
        },
    )

    assert isinstance(config, BaseFalConfig)
    assert config.prompt == "x" * 4096
    assert config.num_inference_steps == 1
    assert config.guidance_scale == guidance_scale
    assert config.output_format == "jpeg"
    assert config.enable_safety_checker is False


@pytest.mark.parametrize(("app_id", "parameters", "expected"), GENERATION_CASES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", "x" * 4097),
        ("num_inference_steps", 0),
        ("num_inference_steps", 51),
        ("guidance_scale", 0.99),
        ("guidance_scale", 20.01),
        ("output_format", "webp"),
        ("enable_safety_checker", None),
        ("extra", True),
    ],
)
def test_iris_z_generation_rejects_invalid_parameters(
    app_id: str,
    parameters: dict[str, object],
    expected: dict[str, object],
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**parameters, field: value})


@pytest.mark.parametrize("app_id", DEPTH_TO_IMAGE_APP_IDS)
@pytest.mark.parametrize("depth_format", ["depth", "disparity", "colorized"])
@pytest.mark.parametrize("resolution", ["512", "1024"])
def test_iris_z_depth_to_image_accepts_depth_formats_and_resolutions(
    app_id: str, depth_format: str, resolution: str
) -> None:
    config = validate_parameters(
        app_id,
        {**DEPTH_TO_IMAGE_PARAMETERS, "depth_format": depth_format, "resolution": resolution},
    )

    assert isinstance(config, BaseFalConfig)
    assert config.depth_format == depth_format
    assert config.resolution == resolution


@pytest.mark.parametrize("app_id", DEPTH_TO_IMAGE_APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [("depth_format", "npy"), ("resolution", "auto"), ("depth_image_url", None)],
)
def test_iris_z_depth_to_image_rejects_invalid_depth_input(
    app_id: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**DEPTH_TO_IMAGE_PARAMETERS, field: value})


@pytest.mark.parametrize("app_id", TEXT_APP_IDS)
@pytest.mark.parametrize(
    "image_size",
    ["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"],
)
def test_iris_z_text_accepts_image_size_presets_and_empty_prompt(
    app_id: str, image_size: str
) -> None:
    config = validate_parameters(app_id, {"prompt": "", "image_size": image_size})

    assert isinstance(config, BaseFalConfig)
    assert config.prompt == ""
    assert config.image_size == image_size


@pytest.mark.parametrize("app_id", TEXT_APP_IDS)
@pytest.mark.parametrize("image_size", [None, "auto"])
def test_iris_z_text_rejects_invalid_image_size_presets(app_id: str, image_size: object) -> None:
    with pytest.raises(ValidationError, match="image_size"):
        validate_parameters(app_id, {**TEXT_PARAMETERS, "image_size": image_size})


@pytest.mark.parametrize(("app_id", "parameters", "expected"), CASES)
def test_iris_z_schema_preserves_required_fields_and_defaults(
    app_id: str, parameters: dict[str, object], expected: dict[str, object]
) -> None:
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    schema = config_class.model_json_schema()

    assert set(schema["required"]) == {"app_id", *parameters}
    assert set(schema["properties"]) == {"app_id", *expected}
    for field, value in expected.items():
        if field not in parameters:
            assert schema["properties"][field]["default"] == value


def test_models_command_lists_all_iris_z_endpoints() -> None:
    assert set(APP_IDS) <= SUPPORTED_APP_IDS
    result = CliRunner().invoke(app, ["models"])

    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", APP_IDS)
def test_schema_command_prints_valid_iris_z_parameters(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    config = validate_parameters(app_id, payload["parameters"])
    assert isinstance(config, BaseFalConfig)
    assert config.app_id == app_id


@pytest.mark.parametrize("app_id", TEXT_APP_IDS)
@pytest.mark.parametrize("image_size", [{}, {"width": 1, "height": 14142}])
def test_iris_z_text_accepts_custom_dimensions_with_openapi_defaults_and_bounds(
    app_id: str, image_size: dict[str, int]
) -> None:
    config = validate_parameters(app_id, {**TEXT_PARAMETERS, "image_size": image_size})

    assert isinstance(config, BaseFalConfig)
    assert config.image_size.model_dump() == {"width": 512, "height": 512, **image_size}


@pytest.mark.parametrize("app_id", TEXT_APP_IDS)
@pytest.mark.parametrize(
    "image_size",
    [
        {"width": 0},
        {"height": 0},
        {"width": 14143},
        {"height": 14143},
        {"width": None},
        {"height": 1.5},
    ],
)
def test_iris_z_text_rejects_custom_dimensions_outside_the_openapi_bounds(
    app_id: str, image_size: dict[str, object]
) -> None:
    with pytest.raises(ValidationError, match="image_size"):
        validate_parameters(app_id, {**TEXT_PARAMETERS, "image_size": image_size})

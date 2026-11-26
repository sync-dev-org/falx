from __future__ import annotations

import pytest
from pydantic import TypeAdapter
from ruamel.yaml import YAML
from typer.testing import CliRunner

import falx.models as models
from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_job_schema,
    validate_parameters,
)

CASES = [
    (
        "fal-ai/vidu/q4/image-to-video",
        "ViduQ4ImageToVideoConfig",
        {"image_url": "https://example.com/start.png"},
    ),
    ("fal-ai/vidu/q4/reference-to-video", "ViduQ4ReferenceToVideoConfig", {"prompt": "Animate."}),
    ("pixverse/v6/max/text-to-video", "PixverseV6MaxTextToVideoConfig", {"prompt": "Animate."}),
    (
        "pixverse/v6/max/image-to-video",
        "PixverseV6MaxImageToVideoConfig",
        {"prompt": "Animate.", "image_url": "https://example.com/start.png"},
    ),
    (
        "fal-ai/kandinsky6-pro/text-to-video",
        "Kandinsky6ProTextToVideoConfig",
        {"prompt": "Animate."},
    ),
    (
        "fal-ai/kandinsky6-pro/image-to-video",
        "Kandinsky6ProImageToVideoConfig",
        {"prompt": "Animate.", "image_url": "https://example.com/start.png"},
    ),
]

runner = CliRunner()
safe_yaml = YAML(typ="safe")


@pytest.mark.parametrize(("app_id", "class_name", "parameters"), CASES)
def test_video_generation_endpoints_are_registered_and_validate_parameters(
    app_id: str, class_name: str, parameters: dict[str, object]
) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    assert config_class is getattr(models, class_name)
    assert config_class.random_seed_field == "seed"
    config = validate_parameters(app_id, parameters)
    assert isinstance(config, config_class)
    assert isinstance(
        TypeAdapter(FalConfig).validate_python({"app_id": app_id, **parameters}), config_class
    )


def test_models_lists_all_six_video_generation_endpoints() -> None:
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert {case[0] for case in CASES} <= set(result.stdout.splitlines())


@pytest.mark.parametrize(("app_id", "class_name", "parameters"), CASES)
def test_schema_prints_valid_job_yaml_for_video_generation_endpoints(
    app_id: str, class_name: str, parameters: dict[str, object]
) -> None:
    result = runner.invoke(app, ["schema", app_id])
    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert validate_job_schema(payload).app_id == app_id
    assert parameters.keys() <= payload["parameters"].keys()
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    config = validate_parameters(app_id, payload["parameters"])
    assert isinstance(config, config_class)
    assert config.model_dump(exclude={"app_id"}) == payload["parameters"]

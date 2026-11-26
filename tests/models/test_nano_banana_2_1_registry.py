from __future__ import annotations

import pytest
from pydantic import TypeAdapter
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx import models
from falx.cli import app
from falx.models import SUPPORTED_APP_IDS, FalConfig, config_class_for_app_id, validate_parameters

APP_IDS = {"google/nano-banana-2.1", "google/nano-banana-2.1/edit"}
runner = CliRunner()


@pytest.mark.parametrize(
    ("app_id", "class_name", "parameters"),
    [
        ("google/nano-banana-2.1", "NanoBanana21Config", {"prompt": "a cat on a mat"}),
        (
            "google/nano-banana-2.1/edit",
            "NanoBanana21EditConfig",
            {"prompt": "make it cinematic", "image_urls": ["https://example.com/input.png"]},
        ),
    ],
)
def test_nano_banana_2_1_registry_routes_and_exports_configs(
    app_id: str, class_name: str, parameters: dict[str, object]
) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = getattr(models, class_name)
    assert class_name in models.__all__
    assert config_class_for_app_id(app_id) is config_class
    assert config_class.random_seed_field == "seed"
    assert isinstance(validate_parameters(app_id, parameters), config_class)
    assert isinstance(
        TypeAdapter(FalConfig).validate_python({"app_id": app_id, **parameters}), config_class
    )


def test_models_command_lists_nano_banana_2_1_endpoints() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    assert set(result.stdout.splitlines()) >= APP_IDS


@pytest.mark.parametrize("app_id", sorted(APP_IDS))
def test_schema_command_prints_nano_banana_2_1_job_yaml(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["slug"] == "<kebab-case-output-slug>"
    assert payload["version"] == 1
    assert payload["parameters"]["thinking_level"] == "medium"
    assert payload["parameters"]["resolution"] == "1K"
    assert payload["parameters"]["prompt"] == "<your prompt here>"
    assert "audio_url" not in payload["parameters"]
    if app_id.endswith("/edit"):
        assert "image_urls" in payload["parameters"]
        assert "video_url" in payload["parameters"]
        assert "pdf_url" in payload["parameters"]
    else:
        assert "image_urls" not in payload["parameters"]

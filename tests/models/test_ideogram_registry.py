from __future__ import annotations

from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    IdeogramV4Config,
    config_class_for_app_id,
)

APP_ID = "ideogram/v4"

runner = CliRunner()
safe_yaml = YAML(typ="safe")


def test_ideogram_app_id_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is IdeogramV4Config


def test_ideogram_v4_config_declares_seed_metadata() -> None:
    assert IdeogramV4Config.random_seed_field == "seed"


def test_models_command_lists_ideogram_v4_app_id() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    assert APP_ID in set(result.stdout.splitlines())


def test_schema_command_prints_ideogram_v4_api_fields() -> None:
    result = runner.invoke(app, ["schema", APP_ID])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == APP_ID
    assert payload["parameters"] == {
        "prompt": "<your prompt here>",
        "expansion_model": "Medium",
        "image_size": "square_hd",
        "rendering_speed": "BALANCED",
        "acceleration": "none",
        "num_images": 1,
        "seed": None,
        "sync_mode": False,
        "enable_safety_checker": True,
        "output_format": "jpeg",
    }

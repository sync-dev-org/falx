from __future__ import annotations

import pytest
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    SeedreamV5ProEditConfig,
    SeedreamV5ProLayerizeConfig,
    SeedreamV5ProTextToImageConfig,
    config_class_for_app_id,
)

APP_IDS = {
    "bytedance/seedream/v5/pro/edit",
    "bytedance/seedream/v5/pro/layerize",
    "bytedance/seedream/v5/pro/text-to-image",
}

runner = CliRunner()
safe_yaml = YAML(typ="safe")


def test_seedream_v5_pro_app_ids_are_registered() -> None:
    assert APP_IDS <= SUPPORTED_APP_IDS
    assert config_class_for_app_id("bytedance/seedream/v5/pro/edit") is SeedreamV5ProEditConfig
    assert (
        config_class_for_app_id("bytedance/seedream/v5/pro/layerize") is SeedreamV5ProLayerizeConfig
    )
    assert (
        config_class_for_app_id("bytedance/seedream/v5/pro/text-to-image")
        is SeedreamV5ProTextToImageConfig
    )


def test_seedream_v5_pro_configs_declare_no_seed_metadata() -> None:
    for app_id in APP_IDS:
        config_class = config_class_for_app_id(app_id)
        assert config_class is not None
        assert config_class.random_seed_field is None


def test_models_command_lists_seedream_v5_pro_app_ids() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    listed_app_ids = set(result.stdout.splitlines())
    assert listed_app_ids >= APP_IDS


@pytest.mark.parametrize(
    ("app_id", "expected_parameters"),
    [
        (
            "bytedance/seedream/v5/pro/edit",
            {
                "prompt": "<your prompt here>",
                "image_size": "auto_2K",
                "num_images": 1,
                "output_format": "jpeg",
                "sync_mode": False,
                "enable_safety_checker": True,
                "image_urls": ["https://example.com/input"],
            },
        ),
        (
            "bytedance/seedream/v5/pro/layerize",
            {
                "prompt": "",
                "image_url": "https://example.com/input",
                "image_size": "auto",
                "sync_mode": False,
                "enable_safety_checker": True,
                "enhance_prompt_mode": "standard",
            },
        ),
        (
            "bytedance/seedream/v5/pro/text-to-image",
            {
                "prompt": "<your prompt here>",
                "image_size": "auto_2K",
                "num_images": 1,
                "output_format": "jpeg",
                "sync_mode": False,
                "enable_safety_checker": True,
            },
        ),
    ],
)
def test_schema_command_prints_seedream_v5_pro_api_fields(
    app_id: str,
    expected_parameters: dict[str, object],
) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"] == expected_parameters

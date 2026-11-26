from __future__ import annotations

import pytest
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    QwenImage3EditConfig,
    QwenImage3TextToImageConfig,
    config_class_for_app_id,
)

APP_IDS = {
    "alibaba/qwen-image-3/edit",
    "alibaba/qwen-image-3/text-to-image",
}

runner = CliRunner()
safe_yaml = YAML(typ="safe")


def test_qwen_image_3_app_ids_are_registered() -> None:
    assert APP_IDS <= SUPPORTED_APP_IDS
    assert config_class_for_app_id("alibaba/qwen-image-3/edit") is QwenImage3EditConfig
    assert (
        config_class_for_app_id("alibaba/qwen-image-3/text-to-image")
        is QwenImage3TextToImageConfig
    )


def test_qwen_image_3_configs_declare_seed_metadata() -> None:
    for app_id in APP_IDS:
        config_class = config_class_for_app_id(app_id)
        assert config_class is not None
        assert config_class.random_seed_field == "seed"


def test_models_command_lists_qwen_image_3_app_ids() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    listed_app_ids = set(result.stdout.splitlines())
    assert listed_app_ids >= APP_IDS


@pytest.mark.parametrize(
    ("app_id", "expected_parameters"),
    [
        (
            "alibaba/qwen-image-3/text-to-image",
            {
                "prompt": "<your prompt here>",
                "negative_prompt": "",
                "image_size": "square_hd",
                "enable_prompt_expansion": True,
                "seed": None,
                "enable_safety_checker": True,
                "sync_mode": False,
                "num_images": 1,
                "output_format": "png",
            },
        ),
        (
            "alibaba/qwen-image-3/edit",
            {
                "prompt": "<your prompt here>",
                "negative_prompt": "",
                "image_size": None,
                "enable_prompt_expansion": True,
                "seed": None,
                "enable_safety_checker": True,
                "sync_mode": False,
                "num_images": 1,
                "output_format": "png",
                "image_urls": ["https://example.com/input"],
            },
        ),
    ],
)
def test_schema_command_prints_qwen_image_3_api_fields(
    app_id: str,
    expected_parameters: dict[str, object],
) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"] == expected_parameters

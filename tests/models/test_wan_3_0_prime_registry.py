from __future__ import annotations

import pytest
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    Wan30PrimeImageToVideoConfig,
    Wan30PrimeReferenceToVideoConfig,
    Wan30PrimeTextToVideoConfig,
    config_class_for_app_id,
)

APP_IDS = {
    "alibaba/wan-3.0-prime/text-to-video",
    "alibaba/wan-3.0-prime/image-to-video",
    "alibaba/wan-3.0-prime/reference-to-video",
}

runner = CliRunner()
safe_yaml = YAML(typ="safe")


def test_wan_3_0_prime_app_ids_are_registered() -> None:
    assert APP_IDS <= SUPPORTED_APP_IDS
    assert (
        config_class_for_app_id("alibaba/wan-3.0-prime/text-to-video")
        is Wan30PrimeTextToVideoConfig
    )
    assert (
        config_class_for_app_id("alibaba/wan-3.0-prime/image-to-video")
        is Wan30PrimeImageToVideoConfig
    )
    assert (
        config_class_for_app_id("alibaba/wan-3.0-prime/reference-to-video")
        is Wan30PrimeReferenceToVideoConfig
    )


def test_wan_3_0_prime_configs_declare_seed_metadata() -> None:
    for app_id in APP_IDS:
        config_class = config_class_for_app_id(app_id)
        assert config_class is not None
        assert config_class.random_seed_field == "seed"


def test_models_command_lists_wan_3_0_prime_app_ids() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    listed_app_ids = set(result.stdout.splitlines())
    assert listed_app_ids >= APP_IDS


@pytest.mark.parametrize(
    ("app_id", "expected_parameters"),
    [
        (
            "alibaba/wan-3.0-prime/text-to-video",
            {
                "prompt": "<your prompt here>",
                "resolution": "1080p",
                "aspect_ratio": "adaptive",
                "duration": 5,
                "audio": True,
                "enable_prompt_expansion": True,
                "enable_thinking": False,
                "seed": None,
                "enable_safety_checker": True,
            },
        ),
        (
            "alibaba/wan-3.0-prime/image-to-video",
            {
                "prompt": None,
                "resolution": "1080p",
                "aspect_ratio": "adaptive",
                "duration": 5,
                "audio": True,
                "enable_prompt_expansion": True,
                "enable_thinking": False,
                "seed": None,
                "enable_safety_checker": True,
                "start_image_url": "https://example.com/input",
                "end_image_url": None,
            },
        ),
        (
            "alibaba/wan-3.0-prime/reference-to-video",
            {
                "prompt": None,
                "resolution": "1080p",
                "aspect_ratio": "adaptive",
                "duration": 5,
                "audio": True,
                "enable_prompt_expansion": True,
                "enable_thinking": False,
                "seed": None,
                "enable_safety_checker": True,
                "reference_image_urls": [],
                "reference_video_urls": [],
                "reference_audio_urls": [],
                "file_url": None,
                "web_url": None,
            },
        ),
    ],
)
def test_schema_command_prints_wan_3_0_prime_api_fields(
    app_id: str,
    expected_parameters: dict[str, object],
) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"] == expected_parameters

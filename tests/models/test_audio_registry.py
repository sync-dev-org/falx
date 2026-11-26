from __future__ import annotations

import pytest
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    MinimaxMusic3Config,
    QwenAudio3TtsConfig,
    SoniloV11VideoToSoundEffectsConfig,
    config_class_for_app_id,
)

APP_CONFIGS = {
    "alibaba/qwen-audio-3-tts": QwenAudio3TtsConfig,
    "minimax/music-3": MinimaxMusic3Config,
    "sonilo/v1.1/video-to-sound-effects": SoniloV11VideoToSoundEffectsConfig,
}

runner = CliRunner()
safe_yaml = YAML(typ="safe")


def test_audio_app_ids_are_registered() -> None:
    assert APP_CONFIGS.keys() <= SUPPORTED_APP_IDS
    for app_id, expected_config_class in APP_CONFIGS.items():
        assert config_class_for_app_id(app_id) is expected_config_class


def test_audio_configs_declare_seed_metadata() -> None:
    assert QwenAudio3TtsConfig.random_seed_field is None
    assert MinimaxMusic3Config.random_seed_field == "seed"
    assert SoniloV11VideoToSoundEffectsConfig.random_seed_field is None


def test_models_command_lists_audio_app_ids() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    assert set(result.stdout.splitlines()) >= APP_CONFIGS.keys()


@pytest.mark.parametrize(
    ("app_id", "expected_parameters"),
    [
        (
            "alibaba/qwen-audio-3-tts",
            {
                "text": "<text>",
                "voice": "Cherry",
                "language": "Auto",
                "enable_safety_checker": True,
            },
        ),
        (
            "minimax/music-3",
            {
                "prompt": "<your prompt here>",
                "lyrics": "<lyrics>",
                "duration": 60.0,
                "seed": None,
                "num_inference_steps": 30,
                "guidance_scale": 1.7,
                "enable_safety_checker": True,
            },
        ),
        (
            "sonilo/v1.1/video-to-sound-effects",
            {
                "video_url": "https://example.com/input",
                "prompt": None,
                "segments": None,
                "audio_format": "aac",
                "keep_speech_vocal": False,
            },
        ),
    ],
)
def test_schema_command_prints_audio_api_fields(
    app_id: str,
    expected_parameters: dict[str, object],
) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"] == expected_parameters

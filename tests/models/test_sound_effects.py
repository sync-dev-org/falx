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

ELEVENLABS = "elevenlabs/sound-effects/v3"
TEXT_AUDIO = "mirelo-ai/sfx2.0/text-to-audio"
VIDEO_AUDIO = "mirelo-ai/sfx2.0/video-to-audio"
VIDEO_VIDEO = "mirelo-ai/sfx2.0/video-to-video"
APP_IDS = (ELEVENLABS, TEXT_AUDIO, VIDEO_AUDIO, VIDEO_VIDEO)
MIRELO_IDS = (TEXT_AUDIO, VIDEO_AUDIO, VIDEO_VIDEO)
AUDIO_IDS = (TEXT_AUDIO, VIDEO_AUDIO)
VIDEO_IDS = (VIDEO_AUDIO, VIDEO_VIDEO)
MP3_BITRATES = (32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320)
OUTPUT_FORMATS = (
    "mp3_22050_32",
    "mp3_44100_32",
    "mp3_44100_64",
    "mp3_44100_96",
    "mp3_44100_128",
    "mp3_44100_192",
    "pcm_8000",
    "pcm_16000",
    "pcm_22050",
    "pcm_24000",
    "pcm_44100",
    "pcm_48000",
    "ulaw_8000",
    "alaw_8000",
    "opus_48000_32",
    "opus_48000_64",
    "opus_48000_96",
    "opus_48000_128",
    "opus_48000_192",
)


def required_parameters(app_id: str) -> dict[str, object]:
    if app_id == ELEVENLABS:
        return {"text": "A wooden door closes."}
    if app_id == TEXT_AUDIO:
        return {"prompt": "A wooden door closes."}
    return {"video_url": "https://example.com/source.mp4"}


def registered_config(app_id: str, **parameters: object) -> BaseFalConfig:
    assert app_id in SUPPORTED_APP_IDS
    config = validate_parameters(app_id, {**required_parameters(app_id), **parameters})
    assert config is not None
    return config


@pytest.mark.parametrize("app_id", APP_IDS)
def test_sound_effects_register_and_preserve_openapi_defaults(app_id: str) -> None:
    config = registered_config(app_id)
    if app_id == ELEVENLABS:
        defaults = {
            "prompt_influence": 0.3,
            "output_format": "mp3_44100_128",
            "duration_seconds": None,
            "loop": False,
            "enable_safety_checker": True,
        }
    else:
        defaults = {
            "num_samples": 2,
            "negative_prompt": None,
            "seed": None,
            "duration": 30 if app_id == TEXT_AUDIO else 10,
        }
        if app_id in AUDIO_IDS:
            defaults.update(upload_audio_format="wav", upload_audio_bitrate_kbps=None)
        if app_id in VIDEO_IDS:
            defaults.update(text_prompt=None, preserve_speech=True)
        if app_id == VIDEO_AUDIO:
            defaults.update(return_speech=False)

    assert config.model_dump() == {"app_id": app_id, **required_parameters(app_id), **defaults}
    assert config_class_for_app_id(app_id) is type(config)
    assert TypeAdapter(FalConfig).validate_python(config.model_dump()) == config
    assert config.random_seed_field == (None if app_id == ELEVENLABS else "seed")


@pytest.mark.parametrize("app_id", APP_IDS)
def test_sound_effects_reject_missing_required_input_and_unknown_fields(app_id: str) -> None:
    registered_config(app_id)
    field = next(iter(required_parameters(app_id)))
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {})
    with pytest.raises(ValidationError, match="unexpected"):
        registered_config(app_id, unexpected=True)


@pytest.mark.parametrize(
    ("app_id", "field", "values"),
    [
        (ELEVENLABS, "text", ["", "x" * 450]),
        (ELEVENLABS, "duration_seconds", [None, 0.5, 30]),
        (ELEVENLABS, "prompt_influence", [0, 1]),
        (ELEVENLABS, "output_format", OUTPUT_FORMATS),
        (ELEVENLABS, "loop", [False, True]),
        (ELEVENLABS, "enable_safety_checker", [False, True]),
        (TEXT_AUDIO, "prompt", ["x", "x" * 2000]),
        (TEXT_AUDIO, "duration", [0.1, 600]),
        (TEXT_AUDIO, "seed", [None, -1, 9223372036854776000]),
    ]
    + [(app_id, "num_samples", [1, 4]) for app_id in MIRELO_IDS]
    + [(app_id, "negative_prompt", [None, "", "x" * 1000]) for app_id in MIRELO_IDS]
    + [(app_id, "upload_audio_format", ["wav", "mp3", "aac", "flac"]) for app_id in AUDIO_IDS]
    + [
        (app_id, field, values)
        for app_id in VIDEO_IDS
        for field, values in [
            ("duration", [1, 600]),
            ("seed", [None, -1, 18446744073709552000]),
            ("text_prompt", [None, "", "x" * 2000]),
            ("preserve_speech", [False, True]),
            ("video_url", ["data:video/mp4;base64,AAAA", ""]),
        ]
    ]
    + [(VIDEO_AUDIO, "return_speech", [False, True])],
)
def test_sound_effects_accept_openapi_limits_enums_and_nulls(
    app_id: str, field: str, values: list[object] | tuple[str, ...]
) -> None:
    for value in values:
        assert registered_config(app_id, **{field: value}).model_dump()[field] == value


@pytest.mark.parametrize(
    ("app_id", "field", "values"),
    [
        (ELEVENLABS, "text", [None, "x" * 451]),
        (ELEVENLABS, "duration_seconds", [0.49, 30.01]),
        (ELEVENLABS, "prompt_influence", [-0.01, 1.01, None]),
        (ELEVENLABS, "output_format", ["wav", None]),
        (ELEVENLABS, "loop", [None]),
        (ELEVENLABS, "enable_safety_checker", [None]),
        (ELEVENLABS, "seed", [1]),
        (TEXT_AUDIO, "prompt", [None, "", "x" * 2001]),
        (TEXT_AUDIO, "duration", [0.09, 600.01, None]),
        (TEXT_AUDIO, "seed", [-2, 9223372036854776001, 0.5]),
    ]
    + [(app_id, "num_samples", [0, 5, 1.5, None]) for app_id in MIRELO_IDS]
    + [(app_id, "negative_prompt", ["x" * 1001]) for app_id in MIRELO_IDS]
    + [(app_id, "upload_audio_format", ["ogg", None]) for app_id in AUDIO_IDS]
    + [
        (app_id, field, values)
        for app_id in VIDEO_IDS
        for field, values in [
            ("duration", [0.99, 600.01, None]),
            ("seed", [-2, 18446744073709552001, 0.5]),
            ("text_prompt", ["x" * 2001]),
            ("preserve_speech", [None]),
            ("video_url", [None]),
        ]
    ]
    + [(VIDEO_AUDIO, "return_speech", [None])]
    + [(VIDEO_VIDEO, "upload_audio_format", ["wav"])]
    + [(VIDEO_VIDEO, "upload_audio_bitrate_kbps", [128])]
    + [(VIDEO_VIDEO, "return_speech", [True])],
)
def test_sound_effects_reject_values_outside_openapi_constraints(
    app_id: str, field: str, values: list[object]
) -> None:
    for value in values:
        with pytest.raises(ValidationError, match=field):
            registered_config(app_id, **{field: value})


@pytest.mark.parametrize("app_id", AUDIO_IDS)
def test_mirelo_accepts_bitrates_allowed_for_each_lossy_audio_format(app_id: str) -> None:
    for audio_format, bitrates in [("mp3", MP3_BITRATES), ("aac", (32, 33, 256))]:
        for bitrate in bitrates:
            config = registered_config(
                app_id, upload_audio_format=audio_format, upload_audio_bitrate_kbps=bitrate
            )
            assert config.upload_audio_bitrate_kbps == bitrate


@pytest.mark.parametrize("app_id", AUDIO_IDS)
@pytest.mark.parametrize(
    ("audio_format", "bitrate"),
    [
        ("wav", 128),
        ("flac", 128),
        ("mp3", 33),
        ("mp3", 31),
        ("mp3", 321),
        ("mp3", 32.5),
        ("aac", 31),
        ("aac", 257),
        ("aac", 320),
    ],
)
def test_mirelo_rejects_bitrate_incompatible_with_audio_format(
    app_id: str, audio_format: str, bitrate: object
) -> None:
    with pytest.raises(ValidationError, match="upload_audio_bitrate_kbps"):
        registered_config(
            app_id, upload_audio_format=audio_format, upload_audio_bitrate_kbps=bitrate
        )


def test_sound_effects_models_command_lists_all_endpoints() -> None:
    result = CliRunner().invoke(app, ["models"])
    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", APP_IDS)
def test_sound_effects_schema_examples_pass_parameter_validation(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0
    job = YAML(typ="safe").load(result.stdout)
    assert job["app_id"] == app_id
    assert validate_parameters(app_id, job["parameters"]) is not None

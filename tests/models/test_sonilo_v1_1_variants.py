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

TEXT_MUSIC = "sonilo/v1.1/text-to-music"
TEXT_SFX = "sonilo/v1.1/text-to-sound-effects"
VIDEO_MUSIC = "sonilo/v1.1/video-to-music"
VIDEO_VIDEO_MUSIC = "sonilo/v1.1/video-to-video-music"
VIDEO_VIDEO_SFX = "sonilo/v1.1/video-to-video-sound-effects"
APP_IDS = (TEXT_MUSIC, TEXT_SFX, VIDEO_MUSIC, VIDEO_VIDEO_MUSIC, VIDEO_VIDEO_SFX)
runner = CliRunner()
safe_yaml = YAML(typ="safe")


def required_parameters(app_id: str) -> dict[str, object]:
    if app_id in (TEXT_MUSIC, TEXT_SFX):
        return {"prompt": "A quiet forest with soft strings."}
    return {"video_url": "https://example.com/source.mp4"}


def expected_parameters(app_id: str) -> dict[str, object]:
    parameters = required_parameters(app_id)
    if app_id == TEXT_MUSIC:
        return {**parameters, "duration": 90, "num_samples": 1}
    if app_id == TEXT_SFX:
        return {**parameters, "duration": 8.0, "audio_format": "aac"}
    if app_id == VIDEO_VIDEO_SFX:
        return {
            **parameters,
            "prompt": None,
            "segments": None,
            "audio_format": "aac",
            "keep_speech_vocal": False,
        }
    parameters.update(
        num_samples=1, prompt=None, prompt_influence=0.5, start_offset=None, duration=None
    )
    if app_id == VIDEO_VIDEO_MUSIC:
        parameters["keep_speech_vocal"] = False
    return parameters


def registered_config(app_id: str, **parameters: object) -> BaseFalConfig:
    assert app_id in SUPPORTED_APP_IDS
    config = validate_parameters(app_id, {**required_parameters(app_id), **parameters})
    assert config is not None
    return config


@pytest.mark.parametrize("app_id", APP_IDS)
def test_sonilo_variants_register_route_and_preserve_openapi_defaults(app_id: str) -> None:
    config = registered_config(app_id)

    assert config_class_for_app_id(app_id) is type(config)
    assert TypeAdapter(FalConfig).validate_python(config.model_dump()) == config
    assert config.random_seed_field is None
    assert config.model_dump() == {"app_id": app_id, **expected_parameters(app_id)}


@pytest.mark.parametrize("app_id", APP_IDS)
def test_sonilo_variants_reject_missing_required_input(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    required_field = "prompt" if app_id in (TEXT_MUSIC, TEXT_SFX) else "video_url"
    with pytest.raises(ValidationError, match=required_field):
        validate_parameters(app_id, {})


@pytest.mark.parametrize("app_id", APP_IDS)
def test_sonilo_variants_reject_unknown_parameters_and_seed(app_id: str) -> None:
    for field in ("unexpected", "seed"):
        with pytest.raises(ValidationError, match=field):
            registered_config(app_id, **{field: 42})


@pytest.mark.parametrize(
    ("app_id", "field", "values"),
    [
        (TEXT_MUSIC, "duration", [1, 600]),
        (TEXT_MUSIC, "num_samples", [1, 3]),
        (TEXT_SFX, "duration", [0.5, 180]),
        (VIDEO_MUSIC, "num_samples", [1, 3]),
        (VIDEO_VIDEO_MUSIC, "num_samples", [1, 3]),
    ]
    + [
        (app_id, field, values)
        for app_id in (VIDEO_MUSIC, VIDEO_VIDEO_MUSIC)
        for field, values in [
            ("duration", [1.0, 600.0, None]),
            ("start_offset", [0.0, 600.0, None]),
            ("prompt_influence", [0.0, 1.0]),
            ("prompt", ["Light piano.", "", None]),
        ]
    ]
    + [
        (app_id, "audio_format", ["wav", "mp3", "aac", "flac"])
        for app_id in (TEXT_SFX, VIDEO_VIDEO_SFX)
    ]
    + [
        (app_id, "keep_speech_vocal", [True, False])
        for app_id in (VIDEO_VIDEO_MUSIC, VIDEO_VIDEO_SFX)
    ],
)
def test_sonilo_variants_accept_enums_nullable_fields_and_numeric_limits(
    app_id: str,
    field: str,
    values: list[object],
) -> None:
    for value in values:
        assert registered_config(app_id, **{field: value}).model_dump()[field] == value


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [(TEXT_MUSIC, "duration", value) for value in (0, 601, 1.5, None)]
    + [(TEXT_MUSIC, "num_samples", value) for value in (0, 4)]
    + [(TEXT_SFX, "duration", value) for value in (0.49, 180.01, None)]
    + [
        (app_id, "num_samples", value)
        for app_id in (VIDEO_MUSIC, VIDEO_VIDEO_MUSIC)
        for value in (0, 4)
    ]
    + [
        (app_id, field, value)
        for app_id in (VIDEO_MUSIC, VIDEO_VIDEO_MUSIC)
        for field, value in [
            ("duration", 0.99),
            ("duration", 600.1),
            ("start_offset", -0.1),
            ("start_offset", 600.1),
            ("prompt_influence", -0.1),
            ("prompt_influence", 1.1),
        ]
    ]
    + [(app_id, "audio_format", "ogg") for app_id in (TEXT_SFX, VIDEO_VIDEO_SFX)]
    + [(app_id, "keep_speech_vocal", None) for app_id in (VIDEO_VIDEO_MUSIC, VIDEO_VIDEO_SFX)]
    + [(VIDEO_MUSIC, "keep_speech_vocal", True)]
    + [(TEXT_SFX, "num_samples", 1)],
)
def test_sonilo_variants_reject_values_outside_openapi_constraints(
    app_id: str,
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError, match=field):
        registered_config(app_id, **{field: value})


def test_sonilo_video_to_video_sound_effects_preserves_segments_and_original_vocals() -> None:
    config = registered_config(
        VIDEO_VIDEO_SFX,
        segments=[{}, {"start": 1, "end": 3.5, "prompt": "A bell rings."}],
        prompt="A quiet village.",
        keep_speech_vocal=True,
        audio_format="flac",
    )

    assert config.model_dump() == {
        "app_id": VIDEO_VIDEO_SFX,
        "video_url": "https://example.com/source.mp4",
        "prompt": "A quiet village.",
        "segments": [
            {"start": 0.0, "end": 0.0, "prompt": ""},
            {"start": 1.0, "end": 3.5, "prompt": "A bell rings."},
        ],
        "audio_format": "flac",
        "keep_speech_vocal": True,
    }


@pytest.mark.parametrize(
    "segments", [[{"start": -0.1}], [{"end": -0.1}], [{"prompt": None}], [{"unexpected": True}]]
)
def test_sonilo_video_to_video_sound_effects_rejects_invalid_segments(segments: object) -> None:
    with pytest.raises(ValidationError, match="segments"):
        registered_config(VIDEO_VIDEO_SFX, segments=segments)


def test_sonilo_models_command_lists_all_variants() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", APP_IDS)
def test_sonilo_schema_examples_contain_valid_required_inputs_and_defaults(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    job = safe_yaml.load(result.stdout)
    expected = expected_parameters(app_id)
    expected.update(
        {"prompt": "<your prompt here>"}
        if app_id in (TEXT_MUSIC, TEXT_SFX)
        else {"video_url": "https://example.com/input"}
    )
    assert job["app_id"] == app_id
    assert job["parameters"] == expected
    assert validate_parameters(app_id, job["parameters"]) is not None

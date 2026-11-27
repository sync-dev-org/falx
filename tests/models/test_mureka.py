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

INSTRUMENTALS = tuple(f"mureka/{version}/generate/instrumental" for version in ("v8", "v9"))
SONGS = tuple(f"mureka/{version}/generate/song" for version in ("v8", "v9"))
SOUNDTRACKS = tuple(f"mureka/{version}/generate/soundtrack" for version in ("v8", "v9"))
TRACK = "mureka/v8/generate/track"
EXTEND = "mureka/v8/song/extend"
REMIX = "mureka/v8/song/remix"
UPLOAD = "mureka/api/files/upload"
SONG_OPERATIONS = (TRACK, EXTEND, REMIX)
APP_IDS = (*INSTRUMENTALS, *SONGS, *SOUNDTRACKS, *SONG_OPERATIONS, UPLOAD)
STYLES = (
    "pop",
    "rock",
    "jazz",
    "r&b",
    "edm",
    "ambient",
    "folk",
    "latin",
    "k-pop",
    "j-pop",
    "house",
    "gospel",
    "lo-fi",
)
TRACK_TYPES = (
    "Vocals",
    "Instrumental",
    "Drums",
    "Bass",
    "Guitar",
    "Keyboard",
    "Percussion",
    "Strings",
    "Synth",
    "FX",
    "Brass",
    "Woodwinds",
)
PURPOSES = (
    "reference",
    "melody",
    "instrumental",
    "voice",
    "audio",
    "remix",
    "soundtrack",
    "lyrics-video",
)


def required_parameters(app_id: str) -> dict[str, object]:
    if app_id in (*INSTRUMENTALS, *SONGS):
        return {"prompt": "Gentle piano at sunrise."}
    if app_id in SOUNDTRACKS:
        return {"image_id": "uploaded-image-id"}
    if app_id == TRACK:
        return {"song_id": "generated-song-id", "generate_type": "Instrumental", "prompt": "Piano"}
    if app_id == EXTEND:
        return {"song_id": "generated-song-id", "lyrics": "Morning light", "extend_at": 0}
    if app_id == REMIX:
        return {"song_id": "generated-song-id", "lyrics": "Morning light", "prompt": "Jazz"}
    assert app_id == UPLOAD
    return {"file_url": "https://example.com/audio.mp3", "purpose": "reference"}


def registered_config(app_id: str, parameters: dict[str, object]) -> BaseFalConfig:
    assert app_id in SUPPORTED_APP_IDS
    config = validate_parameters(app_id, parameters)
    assert config is not None
    return config


@pytest.mark.parametrize("app_id", APP_IDS)
def test_mureka_registers_routes_and_preserves_openapi_defaults(app_id: str) -> None:
    parameters = required_parameters(app_id)
    config = registered_config(app_id, parameters)
    defaults: dict[str, object] = {"enable_safety_checker": True}
    if app_id in INSTRUMENTALS:
        defaults.update(prompt=None, instrumental_id=None)
    elif app_id in SONGS:
        defaults.update(
            lyrics=None,
            melody_id=None,
            vocal_id=None,
            styles=None,
            reference_id=None,
            prompt=None,
            gender=None,
        )
    elif app_id in SOUNDTRACKS:
        defaults.update(video_id=None, audio_start=None, prompt=None, image_id=None, audio_end=None)
    elif app_id in SONG_OPERATIONS:
        defaults.update(song_id=None, upload_audio_id=None)
        if app_id == TRACK:
            defaults.update(lyrics=None, generate_start=None, generate_end=None, vocal_gender=None)
        elif app_id == EXTEND:
            defaults["extend_type"] = "tail"
    else:
        defaults = {}

    assert config.model_dump() == {"app_id": app_id, **defaults, **parameters}
    assert config_class_for_app_id(app_id) is type(config)
    assert TypeAdapter(FalConfig).validate_python(config.model_dump()) == config
    assert config.random_seed_field is None


@pytest.mark.parametrize("app_id", APP_IDS)
def test_mureka_rejects_missing_required_inputs(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    with pytest.raises(ValidationError):
        validate_parameters(app_id, {})


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("field", ("unexpected", "seed"))
def test_mureka_rejects_unrecognized_fields(app_id: str, field: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**required_parameters(app_id), field: 42})


@pytest.mark.parametrize(
    ("app_id", "field", "limit"),
    [(app_id, "prompt", 1024) for app_id in INSTRUMENTALS]
    + [(app_id, "prompt", 2000) for app_id in SONGS]
    + [(app_id, "lyrics", 5000) for app_id in SONGS]
    + [(app_id, "prompt", 1024) for app_id in SOUNDTRACKS]
    + [(TRACK, "prompt", 1024), (TRACK, "lyrics", 5000), (EXTEND, "lyrics", 3000)]
    + [(REMIX, "prompt", 1024), (REMIX, "lyrics", 5000)],
)
def test_mureka_enforces_text_length_boundaries(app_id: str, field: str, limit: int) -> None:
    parameters = required_parameters(app_id)
    if app_id in SONGS and field == "lyrics":
        parameters = {}
    for length in (1, limit):
        config = registered_config(app_id, {**parameters, field: "a" * length})
        assert getattr(config, field) == "a" * length
    for value in ("", "a" * (limit + 1)):
        with pytest.raises(ValidationError, match=field):
            registered_config(app_id, {**parameters, field: value})


@pytest.mark.parametrize("app_id", INSTRUMENTALS)
def test_mureka_instrumental_requires_exactly_one_prompt_or_uploaded_id(app_id: str) -> None:
    config = registered_config(app_id, {"instrumental_id": "uploaded-instrumental-id"})
    assert config.instrumental_id == "uploaded-instrumental-id"
    assert config.prompt is None
    with pytest.raises(ValidationError, match="prompt.*instrumental_id"):
        registered_config(app_id, {"prompt": "Piano", "instrumental_id": "uploaded-id"})
    with pytest.raises(ValidationError, match="instrumental_id"):
        registered_config(app_id, {"instrumental_id": ""})


@pytest.mark.parametrize("app_id", SONGS)
def test_mureka_song_accepts_lyrics_or_prompt_and_limits_style_control(app_id: str) -> None:
    config = registered_config(app_id, {"lyrics": "Sing", "prompt": "a" * 1024})
    assert config.lyrics == "Sing"
    assert config.prompt == "a" * 1024
    with pytest.raises(ValidationError, match="prompt"):
        registered_config(app_id, {"lyrics": "Sing", "prompt": "a" * 1025})
    for gender in ("female", "male"):
        config = registered_config(app_id, {"lyrics": "Sing", "gender": gender})
        assert config.gender == gender
    for style in STYLES:
        config = registered_config(app_id, {"prompt": "Piano", "styles": [style]})
        assert config.styles == [style]
    config = registered_config(app_id, {"prompt": "Piano", "styles": list(STYLES)})
    assert config.styles == list(STYLES)
    for parameters, field in (
        ({"prompt": "Piano", "styles": []}, "styles"),
        ({"prompt": "Piano", "styles": ["unknown"]}, "styles"),
        ({"lyrics": "Sing", "styles": ["pop"]}, "styles"),
        ({"lyrics": "Sing", "gender": "unknown"}, "gender"),
    ):
        with pytest.raises(ValidationError, match=field):
            registered_config(app_id, parameters)


@pytest.mark.parametrize("app_id", SONGS)
def test_mureka_song_preserves_ids_and_rejects_melody_conflicts(app_id: str) -> None:
    config = registered_config(app_id, {"lyrics": "Sing", "melody_id": "uploaded-melody-id"})
    assert config.melody_id == "uploaded-melody-id"
    config = registered_config(
        app_id, {"prompt": "Piano", "reference_id": "uploaded-reference-id", "vocal_id": "voice-id"}
    )
    assert config.reference_id == "uploaded-reference-id"
    assert config.vocal_id == "voice-id"
    for field in ("prompt", "reference_id", "vocal_id"):
        with pytest.raises(ValidationError, match="melody_id"):
            registered_config(app_id, {"lyrics": "Sing", "melody_id": "melody-id", field: "value"})
    for field in ("melody_id", "reference_id", "vocal_id"):
        with pytest.raises(ValidationError, match=field):
            registered_config(app_id, {"lyrics": "Sing", field: ""})


@pytest.mark.parametrize("app_id", SOUNDTRACKS)
def test_mureka_soundtrack_requires_one_uploaded_visual_and_three_second_segment(
    app_id: str,
) -> None:
    config = registered_config(
        app_id, {"video_id": "uploaded-video-id", "audio_start": 1000, "audio_end": 4000}
    )
    assert config.video_id == "uploaded-video-id"
    assert config.image_id is None
    assert config.audio_end - config.audio_start == 3000
    for field in ("audio_start", "audio_end"):
        config = registered_config(app_id, {"image_id": "image-id", field: 0})
        assert getattr(config, field) == 0
    for parameters in (
        {"image_id": "image-id", "video_id": "video-id"},
        {"image_id": ""},
        {"video_id": ""},
        {"image_id": "image-id", "audio_start": 1000, "audio_end": 3999},
    ):
        with pytest.raises(ValidationError):
            registered_config(app_id, parameters)


@pytest.mark.parametrize("app_id", SONG_OPERATIONS)
def test_mureka_song_operations_accept_exactly_one_generated_or_uploaded_id(app_id: str) -> None:
    parameters = required_parameters(app_id)
    parameters.pop("song_id")
    config = registered_config(app_id, {**parameters, "upload_audio_id": "uploaded-audio-id"})
    assert config.song_id is None
    assert config.upload_audio_id == "uploaded-audio-id"
    for source in (
        {},
        {"song_id": None, "upload_audio_id": None},
        {"song_id": "song-id", "upload_audio_id": "upload-id"},
        {"song_id": ""},
        {"upload_audio_id": ""},
    ):
        with pytest.raises(ValidationError, match="song_id|upload_audio_id"):
            registered_config(app_id, {**parameters, **source})


def test_mureka_track_checks_region_dependencies_and_vocal_gender() -> None:
    parameters = required_parameters(TRACK)
    for kind in TRACK_TYPES:
        config = registered_config(TRACK, {**parameters, "generate_type": kind})
        assert config.generate_type == kind
    for gender in ("female", "male"):
        config = registered_config(
            TRACK,
            {
                **parameters,
                "generate_type": "Vocals",
                "vocal_gender": gender,
                "generate_start": 0,
                "generate_end": 1,
            },
        )
        assert config.vocal_gender == gender
        assert config.generate_start == 0
        assert config.generate_end == 1
    for field in ("generate_start", "generate_end"):
        with pytest.raises(ValidationError, match=field):
            registered_config(TRACK, {**parameters, field: -1})
    for changes in (
        {"generate_end": 1},
        {"generate_start": 1, "generate_end": 1},
        {"generate_start": 2, "generate_end": 1},
        {"generate_type": "unknown"},
        {"vocal_gender": "female"},
        {"generate_type": "Vocals", "vocal_gender": "unknown"},
    ):
        with pytest.raises(ValidationError):
            registered_config(TRACK, {**parameters, **changes})


def test_mureka_extension_preserves_direction_and_nonnegative_timestamp() -> None:
    for direction in ("tail", "head"):
        config = registered_config(
            EXTEND, {**required_parameters(EXTEND), "extend_type": direction, "extend_at": 0}
        )
        assert config.extend_type == direction
        assert config.extend_at == 0
    for changes in ({"extend_type": "unknown"}, {"extend_at": -1}):
        with pytest.raises(ValidationError):
            registered_config(EXTEND, {**required_parameters(EXTEND), **changes})


@pytest.mark.parametrize(
    ("app_id", "field"),
    [
        (TRACK, "generate_type"),
        (TRACK, "prompt"),
        (EXTEND, "lyrics"),
        (EXTEND, "extend_at"),
        (REMIX, "lyrics"),
        (REMIX, "prompt"),
        (UPLOAD, "file_url"),
        (UPLOAD, "purpose"),
    ],
)
def test_mureka_rejects_omitted_or_null_required_fields(app_id: str, field: str) -> None:
    parameters = required_parameters(app_id)
    parameters.pop(field)
    for changes in ({}, {field: None}):
        with pytest.raises(ValidationError, match=field):
            registered_config(app_id, {**parameters, **changes})


def test_mureka_upload_accepts_all_purposes_and_data_uris() -> None:
    for purpose in PURPOSES:
        config = registered_config(
            UPLOAD, {"file_url": "data:audio/wav;base64,UklGRg==", "purpose": purpose}
        )
        assert config.file_url == "data:audio/wav;base64,UklGRg=="
        assert config.purpose == purpose
    with pytest.raises(ValidationError, match="purpose"):
        registered_config(UPLOAD, {**required_parameters(UPLOAD), "purpose": "unknown"})


@pytest.mark.parametrize("app_id", APP_IDS)
def test_mureka_models_listing_and_schema_examples_are_valid(app_id: str) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert app_id in result.stdout.splitlines()
    result = runner.invoke(app, ["schema", app_id])
    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    assert payload["app_id"] == app_id
    config = registered_config(app_id, payload["parameters"])
    assert config.app_id == app_id

from __future__ import annotations

from typing import Any

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

SEED_APP_ID = "bytedance/seed-tts/v3"
HEYGEN_APP_IDS = ["heygen/heygen-voice", "heygen/heygen-voice/turbo"]
KOTOBA_APP_ID = "kotoba-technologies/kotoba-stt/v1/speech-to-text"
APP_PARAMETERS = {
    SEED_APP_ID: {"text": "Hello."},
    **{app_id: {"text": "Hello."} for app_id in HEYGEN_APP_IDS},
    KOTOBA_APP_ID: {"audio_url": "https://example.com/speech.wav", "language": "ja"},
}
SAMPLE_RATES = [8000, 16000, 22050, 24000, 32000, 44100, 48000]
HEYGEN_VOICES = [
    "Jonah",
    "Nadine",
    "Tabitha",
    "Soren",
    "Elowen",
    "Vincent",
    "Jocelyn",
    "Marielle",
    "Corinne",
    "Lucian",
    "Kieran",
    "Hugh",
    "Noelle",
    "Bram",
    "Ewan",
    "Iona",
    "Cecily",
    "Simon",
    "Weston",
    "Felicity",
    "Gareth",
    "Rory",
    "Meredith",
    "Sabrina",
]
HEYGEN_LANGUAGES = [
    "ar",
    "be",
    "bg",
    "ca",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "fa",
    "fi",
    "fr",
    "he",
    "hi",
    "hr",
    "hu",
    "id",
    "it",
    "ja",
    "ko",
    "mk",
    "ms",
    "nl",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sr",
    "sv",
    "ta",
    "th",
    "tl",
    "tr",
    "uk",
    "vi",
    "zh",
]
KOTOBA_LANGUAGES = ["ja", "en", "ko", "zh", "es", "zh-hk", "zh-tw", "auto"]


def _config_class(app_id: str) -> type[BaseFalConfig]:
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None, f"Missing configuration for {app_id}"
    return config_class


def _config(app_id: str, **parameters: Any) -> BaseFalConfig:
    return _config_class(app_id).model_validate({"app_id": app_id, **parameters})


@pytest.mark.parametrize("app_id", APP_PARAMETERS)
def test_speech_models_register_and_validate_job_parameters(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = _config_class(app_id)
    assert config_class.random_seed_field is None
    config = validate_parameters(app_id, APP_PARAMETERS[app_id])
    assert isinstance(config, config_class)
    parsed = TypeAdapter(FalConfig).validate_python({"app_id": app_id, **APP_PARAMETERS[app_id]})
    assert parsed == config


@pytest.mark.parametrize("app_id", APP_PARAMETERS)
def test_models_and_schema_commands_expose_valid_speech_parameters(app_id: str) -> None:
    runner = CliRunner()
    listing = runner.invoke(app, ["models"])
    assert listing.exit_code == 0
    assert app_id in listing.stdout.splitlines()
    result = runner.invoke(app, ["schema", app_id])
    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    assert payload["app_id"] == app_id
    assert isinstance(validate_parameters(app_id, payload["parameters"]), _config_class(app_id))


def test_seed_tts_v3_defaults() -> None:
    assert _config(SEED_APP_ID, text="Hello.").model_dump() == {
        "app_id": SEED_APP_ID,
        "text": "Hello.",
        "voice": "stokie_en",
        "language": None,
        "voice_instruction": None,
        "speed": 1,
        "volume": 1,
        "pitch": 0,
        "output_format": "mp3",
        "sample_rate": None,
    }


@pytest.mark.parametrize("bound", [0, 1])
def test_seed_tts_v3_accepts_text_and_numeric_boundaries(bound: int) -> None:
    parameters = {
        "text": ["x", "x" * 10000][bound],
        "voice": "saki_ja",
        "language": "ja",
        "voice_instruction": "Warm and natural",
        "speed": [0.5, 2][bound],
        "volume": [0.5, 2][bound],
        "pitch": [-12, 12][bound],
        "output_format": "opus",
        "sample_rate": 48000,
    }
    assert _config(SEED_APP_ID, **parameters).model_dump() == {
        "app_id": SEED_APP_ID,
        **parameters,
    }


@pytest.mark.parametrize("sample_rate", [*SAMPLE_RATES, None])
def test_seed_tts_v3_accepts_documented_sample_rates(sample_rate: int | None) -> None:
    config = _config(SEED_APP_ID, text="Hello.", sample_rate=sample_rate)
    assert config.model_dump()["sample_rate"] == sample_rate


@pytest.mark.parametrize(
    ("voice", "language"),
    [
        ("owen_en", "en"),
        ("pigsy_zh", "zh-CN-x-sichuan"),
        ("kenta_ja", "ja"),
        ("jiwoo_ko", "ko"),
        ("rania_ar", "ar"),
        ("stokie_en", "zu"),
    ],
)
def test_seed_tts_v3_accepts_multilingual_voices(voice: str, language: str) -> None:
    config = _config(SEED_APP_ID, text="Hello.", voice=voice, language=language)
    assert config.model_dump()["voice"] == voice
    assert config.model_dump()["language"] == language


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("text", ""),
        ("text", "x" * 10001),
        ("text", None),
        ("voice", "unknown"),
        ("voice", None),
        ("language", "invalid"),
        ("voice_instruction", ""),
        ("speed", 0.49),
        ("speed", 2.01),
        ("speed", None),
        ("volume", 0.49),
        ("volume", 2.01),
        ("volume", None),
        ("pitch", -13),
        ("pitch", 13),
        ("pitch", 0.5),
        ("pitch", None),
        ("output_format", "wav"),
        ("output_format", None),
        ("sample_rate", 12345),
    ],
)
def test_seed_tts_v3_rejects_invalid_parameters(field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        _config(SEED_APP_ID, **{"text": "Hello.", field: value})


def test_seed_tts_v3_schema_preserves_api_constraints() -> None:
    schema = _config_class(SEED_APP_ID).model_json_schema()
    assert schema["required"] == ["app_id", "text"]
    properties = schema["properties"]
    assert properties["text"]["minLength"] == 1
    assert properties["text"]["maxLength"] == 10000
    assert len(properties["voice"]["enum"]) == 520
    assert len(properties["language"]["anyOf"][0]["enum"]) == 119
    assert properties["voice_instruction"]["anyOf"][0]["minLength"] == 1
    assert properties["sample_rate"]["anyOf"][0]["enum"] == SAMPLE_RATES
    assert properties["output_format"]["enum"] == ["mp3", "opus"]
    for name in ("speed", "volume"):
        assert properties[name]["minimum"] == 0.5
        assert properties[name]["maximum"] == 2
    assert properties["pitch"]["minimum"] == -12
    assert properties["pitch"]["maximum"] == 12


@pytest.mark.parametrize("app_id", HEYGEN_APP_IDS)
def test_heygen_voice_defaults_and_cloning_parameters(app_id: str) -> None:
    assert _config(app_id, text="Hello.").model_dump() == {
        "app_id": app_id,
        "text": "Hello.",
        "voice": "Jonah",
        "reference_audio_url": None,
        "language": None,
        "expressiveness_boost": 1,
        "enable_safety_checker": True,
    }
    parameters = {
        "text": "x" * 5000,
        "voice": "Sabrina",
        "reference_audio_url": "https://example.com/voice.wav",
        "language": "ja",
        "expressiveness_boost": 0,
        "enable_safety_checker": False,
    }
    assert _config(app_id, **parameters).model_dump() == {"app_id": app_id, **parameters}


@pytest.mark.parametrize("app_id", HEYGEN_APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        *(("voice", value) for value in HEYGEN_VOICES),
        *(("language", value) for value in HEYGEN_LANGUAGES),
    ],
)
def test_heygen_voice_accepts_documented_voice_and_language_choices(
    app_id: str,
    field: str,
    value: str,
) -> None:
    assert _config(app_id, text="Hello.", **{field: value}).model_dump()[field] == value


@pytest.mark.parametrize("app_id", HEYGEN_APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("text", ""),
        ("text", "x" * 5001),
        ("text", None),
        ("voice", "unknown"),
        ("voice", None),
        ("language", "auto"),
        ("reference_audio_url", []),
        ("expressiveness_boost", -0.01),
        ("expressiveness_boost", 1.01),
        ("expressiveness_boost", None),
        ("enable_safety_checker", None),
    ],
)
def test_heygen_voice_rejects_invalid_parameters(app_id: str, field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        _config(app_id, **{"text": "Hello.", field: value})


@pytest.mark.parametrize("app_id", HEYGEN_APP_IDS)
def test_heygen_voice_schema_preserves_api_choices_and_bounds(app_id: str) -> None:
    schema = _config_class(app_id).model_json_schema()
    assert schema["required"] == ["app_id", "text"]
    properties = schema["properties"]
    assert properties["text"]["minLength"] == 1
    assert properties["text"]["maxLength"] == 5000
    assert properties["voice"]["enum"] == HEYGEN_VOICES
    assert properties["language"]["anyOf"][0]["enum"] == HEYGEN_LANGUAGES
    assert properties["expressiveness_boost"]["minimum"] == 0
    assert properties["expressiveness_boost"]["maximum"] == 1


def test_kotoba_stt_defaults() -> None:
    assert _config(KOTOBA_APP_ID, **APP_PARAMETERS[KOTOBA_APP_ID]).model_dump() == {
        "app_id": KOTOBA_APP_ID,
        "audio_url": "https://example.com/speech.wav",
        "language": "ja",
        "with_timestamps": False,
        "diarization": False,
        "keywords": None,
        "kana": False,
    }


def test_kotoba_stt_accepts_keyword_boundaries_and_optional_output_settings() -> None:
    parameters = {
        "audio_url": "data:audio/wav;base64,UklGRg==",
        "language": "auto",
        "with_timestamps": True,
        "diarization": True,
        "keywords": ["あ" * 64] * 1000,
        "kana": True,
    }
    assert _config(KOTOBA_APP_ID, **parameters).model_dump() == {
        "app_id": KOTOBA_APP_ID,
        **parameters,
    }


@pytest.mark.parametrize("language", KOTOBA_LANGUAGES)
def test_kotoba_stt_accepts_documented_languages(language: str) -> None:
    parameters = {**APP_PARAMETERS[KOTOBA_APP_ID], "language": language}
    assert _config(KOTOBA_APP_ID, **parameters).model_dump()["language"] == language


@pytest.mark.parametrize("keywords", [None, [], [""]])
def test_kotoba_stt_accepts_empty_keyword_inputs_and_diarization_without_times(
    keywords: list[str] | None,
) -> None:
    config = _config(
        KOTOBA_APP_ID, **APP_PARAMETERS[KOTOBA_APP_ID], keywords=keywords, diarization=True
    )
    assert config.model_dump()["keywords"] == keywords
    assert config.model_dump()["with_timestamps"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("audio_url", None),
        ("language", "fr"),
        ("language", None),
        ("keywords", ["x"] * 1001),
        ("keywords", ["x" * 65]),
        ("keywords", [1]),
        ("with_timestamps", None),
        ("diarization", None),
        ("kana", None),
    ],
)
def test_kotoba_stt_rejects_invalid_parameters(field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        _config(KOTOBA_APP_ID, **{**APP_PARAMETERS[KOTOBA_APP_ID], field: value})


def test_kotoba_stt_schema_preserves_required_fields_and_keyword_limits() -> None:
    schema = _config_class(KOTOBA_APP_ID).model_json_schema()
    assert schema["required"] == ["app_id", "audio_url", "language"]
    assert schema["properties"]["language"]["enum"] == KOTOBA_LANGUAGES
    keywords = schema["properties"]["keywords"]["anyOf"][0]
    assert keywords["maxItems"] == 1000
    assert keywords["items"] == {"type": "string", "maxLength": 64}


@pytest.mark.parametrize(
    ("app_id", "field"),
    [
        (SEED_APP_ID, "text"),
        *((app_id, "text") for app_id in HEYGEN_APP_IDS),
        (KOTOBA_APP_ID, "audio_url"),
        (KOTOBA_APP_ID, "language"),
    ],
)
def test_speech_models_reject_missing_required_parameters(app_id: str, field: str) -> None:
    parameters = {name: value for name, value in APP_PARAMETERS[app_id].items() if name != field}
    with pytest.raises(ValidationError, match=field):
        _config(app_id, **parameters)


@pytest.mark.parametrize("app_id", APP_PARAMETERS)
def test_speech_models_reject_unrecognized_parameters(app_id: str) -> None:
    with pytest.raises(ValidationError, match="unexpected"):
        _config(app_id, **APP_PARAMETERS[app_id], unexpected=True)

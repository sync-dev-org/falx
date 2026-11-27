from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

STANDARD = "veed/dubbing"
PRO = "veed/dubbing/pro"
APP_IDS = (STANDARD, PRO)
VIDEO_URL = "https://example.com/speech.mp4"
STANDARD_LANGUAGES = [
    "af",
    "ar",
    "as",
    "ast",
    "az",
    "be",
    "bg",
    "bn",
    "bs",
    "ca",
    "ceb",
    "cs",
    "cy",
    "da",
    "de",
    "el",
    "en",
    "es",
    "et",
    "fa",
    "fi",
    "fil",
    "fr",
    "ga",
    "gl",
    "gu",
    "ha",
    "he",
    "hi",
    "hr",
    "hu",
    "hy",
    "id",
    "is",
    "it",
    "ja",
    "jv",
    "ka",
    "kk",
    "kn",
    "ko",
    "ky",
    "lb",
    "ln",
    "lt",
    "lv",
    "mi",
    "mk",
    "ml",
    "mn",
    "mr",
    "ms",
    "mt",
    "my",
    "ne",
    "nl",
    "no",
    "ny",
    "oc",
    "or",
    "pa",
    "pl",
    "ps",
    "pt",
    "ro",
    "ru",
    "sd",
    "sk",
    "sl",
    "so",
    "sr",
    "sv",
    "sw",
    "ta",
    "te",
    "tg",
    "th",
    "tl",
    "tr",
    "uk",
    "ur",
    "uz",
    "vi",
    "yo",
    "yue",
    "zh",
]
PRO_SOURCE_LANGUAGES = [
    "af",
    "ak",
    "am",
    "ar",
    "as",
    "az",
    "be",
    "bg",
    "bo",
    "bs",
    "ca",
    "ceb",
    "cmn",
    "cs",
    "cy",
    "da",
    "de",
    "dgo",
    "el",
    "en",
    "es",
    "et",
    "eu",
    "fa",
    "fi",
    "fil",
    "fr",
    "gl",
    "gu",
    "ha",
    "he",
    "hi",
    "hr",
    "hu",
    "hy",
    "id",
    "is",
    "it",
    "ja",
    "jv",
    "ka",
    "ki",
    "kk",
    "kn",
    "ko",
    "ky",
    "lg",
    "lt",
    "lv",
    "mk",
    "ml",
    "mn",
    "mr",
    "ms",
    "my",
    "ne",
    "nl",
    "no",
    "nso",
    "pa",
    "pl",
    "pt",
    "rn",
    "ro",
    "ru",
    "rw",
    "sd",
    "sk",
    "sl",
    "sq",
    "ss",
    "st",
    "su",
    "sv",
    "sw",
    "ta",
    "te",
    "tg",
    "th",
    "tn",
    "tr",
    "ts",
    "ug",
    "uk",
    "ur",
    "uz",
    "ve",
    "vi",
    "war",
    "wo",
    "yo",
    "yue",
    "zh",
    "zu",
]
PRO_TARGET_LANGUAGES = [
    *PRO_SOURCE_LANGUAGES,
    "ar-EG",
    "en-AU",
    "en-CA",
    "en-GB",
    "en-US",
    "es-AR",
    "es-CL",
    "es-ES",
    "es-MX",
    "fr-CA",
    "fr-FR",
    "pt-BR",
    "pt-PT",
    "zh-TW",
]


@pytest.mark.parametrize("app_id", APP_IDS)
def test_veed_dubbing_registers_and_preserves_input_defaults(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config = validate_parameters(app_id, {"video_url": VIDEO_URL, "target_language": "es"})
    assert config is not None
    assert type(config) is config_class_for_app_id(app_id)
    assert TypeAdapter(FalConfig).validate_python(config.model_dump()) == config
    assert config.random_seed_field is None
    expected = {
        "app_id": app_id,
        "video_url": VIDEO_URL,
        "target_language": "es",
        "source_language": "auto",
        "keyterms": [],
    }
    if app_id == PRO:
        expected["voice_cloning_strength"] = 7
    assert config.model_dump() == expected


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("missing", ["video_url", "target_language"])
def test_veed_dubbing_requires_video_and_target_language(app_id: str, missing: str) -> None:
    parameters = {"video_url": VIDEO_URL, "target_language": "es"}
    del parameters[missing]
    assert app_id in SUPPORTED_APP_IDS
    with pytest.raises(ValidationError, match=missing):
        validate_parameters(app_id, parameters)


@pytest.mark.parametrize("app_id", APP_IDS)
def test_veed_dubbing_accepts_all_declared_languages(app_id: str) -> None:
    targets = STANDARD_LANGUAGES if app_id == STANDARD else PRO_TARGET_LANGUAGES
    sources = STANDARD_LANGUAGES if app_id == STANDARD else PRO_SOURCE_LANGUAGES
    for field, languages in (("target_language", targets), ("source_language", ["auto", *sources])):
        for language in languages:
            config = validate_parameters(
                app_id, {"video_url": VIDEO_URL, "target_language": "es", field: language}
            )
            assert config is not None
            assert config.model_dump()[field] == language
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    properties = config_class.model_json_schema()["properties"]
    assert set(properties["target_language"]["enum"]) == set(targets)
    assert set(properties["source_language"]["enum"]) == {"auto", *sources}


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("video_url", "x" * 2083),
        ("video_url", "x"),
        ("keyterms", ["x" * 50]),
        ("keyterms", ["one two three four five"]),
        ("keyterms", ["brand"] * 1000),
        ("keyterms", [""]),
    ],
)
def test_veed_dubbing_accepts_video_length_and_keyterm_limits(
    app_id: str, field: str, value: object
) -> None:
    config = validate_parameters(
        app_id, {"video_url": VIDEO_URL, "target_language": "es", field: value}
    )
    assert config is not None
    assert config.model_dump()[field] == value


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("video_url", ""),
        ("video_url", "x" * 2084),
        ("video_url", None),
        ("target_language", "auto"),
        ("target_language", "invalid"),
        ("source_language", "invalid"),
        ("source_language", "es-MX"),
        ("keyterms", ["x" * 51]),
        ("keyterms", ["one two three four five six"]),
        ("keyterms", ["brand"] * 1001),
        ("keyterms", None),
        ("keyterms", "brand"),
        ("seed", 42),
        ("unexpected", True),
        *(("keyterms", [f"brand{character}"]) for character in "<>{}[]\\"),
    ],
)
def test_veed_dubbing_rejects_values_outside_input_constraints(
    app_id: str, field: str, value: object
) -> None:
    assert app_id in SUPPORTED_APP_IDS
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {"video_url": VIDEO_URL, "target_language": "es", field: value})


@pytest.mark.parametrize("value", [0, 10])
def test_veed_dubbing_pro_accepts_voice_cloning_strength_limits(value: int) -> None:
    config = validate_parameters(
        PRO, {"video_url": VIDEO_URL, "target_language": "es", "voice_cloning_strength": value}
    )
    assert config is not None
    assert config.voice_cloning_strength == value


@pytest.mark.parametrize("value", [-1, 11, 0.5, None])
def test_veed_dubbing_pro_rejects_invalid_voice_cloning_strength(value: object) -> None:
    assert PRO in SUPPORTED_APP_IDS
    with pytest.raises(ValidationError, match="voice_cloning_strength"):
        validate_parameters(
            PRO, {"video_url": VIDEO_URL, "target_language": "es", "voice_cloning_strength": value}
        )


@pytest.mark.parametrize(
    "parameters", [{"target_language": "es-MX"}, {"voice_cloning_strength": 7}]
)
def test_standard_dubbing_rejects_pro_only_options(parameters: dict[str, object]) -> None:
    assert STANDARD in SUPPORTED_APP_IDS
    with pytest.raises(ValidationError):
        validate_parameters(
            STANDARD, {"video_url": VIDEO_URL, "target_language": "es", **parameters}
        )


@pytest.mark.parametrize("app_id", APP_IDS)
def test_veed_dubbing_exposes_video_and_keyterm_bounds(app_id: str) -> None:
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    schema = config_class.model_json_schema()
    assert set(schema["required"]) == {"app_id", "video_url", "target_language"}
    properties = schema["properties"]
    assert properties["video_url"]["minLength"] == 1
    assert properties["video_url"]["maxLength"] == 2083
    assert properties["video_url"]["format"] == "uri"
    assert properties["keyterms"]["maxItems"] == 1000
    assert properties["keyterms"]["items"]["maxLength"] == 50

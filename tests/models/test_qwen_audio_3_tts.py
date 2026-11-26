from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import QwenAudio3TtsConfig

APP_ID = "alibaba/qwen-audio-3-tts"

VOICES = [
    "Cherry",
    "Serena",
    "Ethan",
    "Chelsie",
    "Momo",
    "Vivian",
    "Moon",
    "Maia",
    "Kai",
    "Nofish",
    "Bella",
    "Jennifer",
    "Ryan",
    "Katerina",
    "Aiden",
    "Mia",
    "Mochi",
    "Bellona",
    "Vincent",
    "Bunny",
    "Neil",
    "Elias",
    "Arthur",
    "Nini",
    "Seren",
    "Pip",
    "Stella",
    "Bodega",
    "Sonrisa",
    "Alek",
    "Dolce",
    "Sohee",
    "Lenn",
    "Emilien",
    "Andre",
    "Jada",
    "Dylan",
    "Li",
    "Marcus",
    "Roy",
    "Peter",
    "Sunny",
    "Eric",
    "Rocky",
    "Kiki",
]

LANGUAGES = [
    "Auto",
    "Chinese",
    "English",
    "Spanish",
    "Russian",
    "Italian",
    "French",
    "Korean",
    "Japanese",
    "German",
    "Portuguese",
]


def test_qwen_audio_3_tts_accepts_schema_defaults() -> None:
    config = QwenAudio3TtsConfig(app_id=APP_ID, text="Hello from falx.")

    assert config.model_dump() == {
        "app_id": APP_ID,
        "text": "Hello from falx.",
        "voice": "Cherry",
        "language": "Auto",
    }


def test_qwen_audio_3_tts_accepts_all_fields() -> None:
    config = QwenAudio3TtsConfig(
        app_id=APP_ID,
        text="こんにちは。",
        voice="Kiki",
        language="Japanese",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "text": "こんにちは。",
        "voice": "Kiki",
        "language": "Japanese",
    }


def test_qwen_audio_3_tts_schema_matches_openapi_contract() -> None:
    schema = QwenAudio3TtsConfig.model_json_schema()

    assert schema["required"] == ["app_id", "text"]
    assert schema["properties"]["text"]["minLength"] == 1
    assert schema["properties"]["text"]["maxLength"] == 2000
    assert schema["properties"]["text"]["description"] == "The text to convert to speech."
    assert schema["properties"]["voice"]["default"] == "Cherry"
    assert schema["properties"]["voice"]["enum"] == VOICES
    assert schema["properties"]["voice"]["description"] == (
        "The voice used for speech synthesis. See the [Qwen-TTS voice list]"
        "(https://www.alibabacloud.com/help/en/model-studio/qwen-tts-voice-list) "
        "for each voice's language and dialect coverage."
    )
    assert schema["properties"]["language"]["default"] == "Auto"
    assert schema["properties"]["language"]["enum"] == LANGUAGES
    assert schema["properties"]["language"]["description"] == (
        "Language of the input text. `Auto` lets the model detect it; setting it "
        "explicitly improves pronunciation and intonation."
    )


@pytest.mark.parametrize("voice", VOICES)
def test_qwen_audio_3_tts_accepts_voice_enum(voice: str) -> None:
    config = QwenAudio3TtsConfig(app_id=APP_ID, text="Hello.", voice=voice)

    assert config.voice == voice


@pytest.mark.parametrize("language", LANGUAGES)
def test_qwen_audio_3_tts_accepts_language_enum(language: str) -> None:
    config = QwenAudio3TtsConfig(app_id=APP_ID, text="Hello.", language=language)

    assert config.language == language


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID}, "text"),
        ({"app_id": APP_ID, "text": ""}, "text"),
        ({"app_id": APP_ID, "text": "x" * 2001}, "text"),
        ({"app_id": APP_ID, "text": "Hello.", "voice": "Unknown"}, "voice"),
        ({"app_id": APP_ID, "text": "Hello.", "language": "Dutch"}, "language"),
        ({"app_id": APP_ID, "text": "Hello.", "voice": None}, "voice"),
        ({"app_id": APP_ID, "text": "Hello.", "language": None}, "language"),
        ({"app_id": APP_ID, "text": "Hello.", "unexpected": True}, "unexpected"),
    ],
)
def test_qwen_audio_3_tts_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        QwenAudio3TtsConfig.model_validate(payload)

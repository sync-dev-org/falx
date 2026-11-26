from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class QwenAudio3TtsConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["alibaba/qwen-audio-3-tts"]
    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The text to convert to speech.",
    )
    voice: Literal[
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
    ] = Field(
        default="Cherry",
        description=(
            "The voice used for speech synthesis. See the [Qwen-TTS voice list]"
            "(https://www.alibabacloud.com/help/en/model-studio/qwen-tts-voice-list) "
            "for each voice's language and dialect coverage."
        ),
    )
    language: Literal[
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
    ] = Field(
        default="Auto",
        description=(
            "Language of the input text. `Auto` lets the model detect it; setting it "
            "explicitly improves pronunciation and intonation."
        ),
    )

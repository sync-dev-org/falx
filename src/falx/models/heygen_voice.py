from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class HeygenVoiceConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["heygen/heygen-voice", "heygen/heygen-voice/turbo"]
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The text to speak.",
    )
    voice: Literal[
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
    ] = Field(
        default="Jonah",
        description="HeyGen public voice. Ignored when reference_audio_url is set.",
    )
    reference_audio_url: str | None = Field(
        default=None,
        description=(
            "Recording of a single speaker to clone instead of using a public voice. "
            "Only the first 3 minutes are used."
        ),
    )
    language: (
        Literal[
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
        | None
    ) = Field(
        default=None,
        description="Language of the text. Detected from the text when omitted.",
    )
    expressiveness_boost: float = Field(
        default=1,
        ge=0,
        le=1,
        description="How expressive the delivery is.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

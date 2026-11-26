from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

GeminiTtsVoice = Literal[
    "Achernar",
    "Achird",
    "Algenib",
    "Algieba",
    "Alnilam",
    "Aoede",
    "Autonoe",
    "Callirrhoe",
    "Charon",
    "Despina",
    "Enceladus",
    "Erinome",
    "Fenrir",
    "Gacrux",
    "Iapetus",
    "Kore",
    "Laomedeia",
    "Leda",
    "Orus",
    "Pulcherrima",
    "Puck",
    "Rasalgethi",
    "Sadachbia",
    "Sadaltager",
    "Schedar",
    "Sulafat",
    "Umbriel",
    "Vindemiatrix",
    "Zephyr",
    "Zubenelgenubi",
]

GeminiTtsLanguage = Literal[
    "Arabic (Egypt)",
    "Bangla (Bangladesh)",
    "Dutch (Netherlands)",
    "English (India)",
    "English (US)",
    "French (France)",
    "German (Germany)",
    "Hindi (India)",
    "Indonesian (Indonesia)",
    "Italian (Italy)",
    "Japanese (Japan)",
    "Korean (South Korea)",
    "Marathi (India)",
    "Polish (Poland)",
    "Portuguese (Brazil)",
    "Romanian (Romania)",
    "Russian (Russia)",
    "Spanish (Spain)",
    "Tamil (India)",
    "Telugu (India)",
    "Thai (Thailand)",
    "Turkish (Turkey)",
    "Ukrainian (Ukraine)",
    "Vietnamese (Vietnam)",
    "Afrikaans (South Africa)",
    "Albanian (Albania)",
    "Amharic (Ethiopia)",
    "Arabic (World)",
    "Armenian (Armenia)",
    "Azerbaijani (Azerbaijan)",
    "Basque (Spain)",
    "Belarusian (Belarus)",
    "Bulgarian (Bulgaria)",
    "Burmese (Myanmar)",
    "Catalan (Spain)",
    "Cebuano (Philippines)",
    "Chinese Mandarin (China)",
    "Chinese Mandarin (Taiwan)",
    "Croatian (Croatia)",
    "Czech (Czech Republic)",
    "Danish (Denmark)",
    "English (Australia)",
    "English (UK)",
    "Estonian (Estonia)",
    "Filipino (Philippines)",
    "Finnish (Finland)",
    "French (Canada)",
    "Galician (Spain)",
    "Georgian (Georgia)",
    "Greek (Greece)",
    "Gujarati (India)",
    "Haitian Creole (Haiti)",
    "Hebrew (Israel)",
    "Hungarian (Hungary)",
    "Icelandic (Iceland)",
    "Javanese (Java)",
    "Kannada (India)",
    "Konkani (India)",
    "Lao (Laos)",
    "Latin (Vatican City)",
    "Latvian (Latvia)",
    "Lithuanian (Lithuania)",
    "Luxembourgish (Luxembourg)",
    "Macedonian (North Macedonia)",
    "Maithili (India)",
    "Malagasy (Madagascar)",
    "Malay (Malaysia)",
    "Malayalam (India)",
    "Mongolian (Mongolia)",
    "Nepali (Nepal)",
    "Norwegian Bokmal (Norway)",
    "Norwegian Nynorsk (Norway)",
    "Odia (India)",
    "Pashto (Afghanistan)",
    "Persian (Iran)",
    "Portuguese (Portugal)",
    "Punjabi (India)",
    "Serbian (Serbia)",
    "Sindhi (India)",
    "Sinhala (Sri Lanka)",
    "Slovak (Slovakia)",
    "Slovenian (Slovenia)",
    "Spanish (Latin America)",
    "Spanish (Mexico)",
    "Swahili (Kenya)",
    "Swedish (Sweden)",
    "Urdu (Pakistan)",
]


class GeminiTtsSpeaker(BaseFalConfig):
    """Voice configuration for a single speaker in multi-speaker synthesis."""

    voice: GeminiTtsVoice = Field(
        ...,
        description="Voice preset for this speaker.",
    )
    speaker_id: str = Field(
        ...,
        pattern="^\\w+$",
        description=(
            "Alias used to identify this speaker in the prompt. Use this alias as a prefix in "
            "the prompt field, e.g. 'Alice: Hello! Bob: Hi there!'. Must be alphanumeric with "
            "no whitespace."
        ),
    )


class Gemini38TtsSpeaker(BaseFalConfig):
    speaker_id: str = Field(
        ...,
        min_length=1,
        description="Speaker alias used in each turn.",
    )
    voice: GeminiTtsVoice = Field(
        ...,
        description="Prebuilt voice for this speaker.",
    )


class Gemini38SpeechTurn(BaseFalConfig):
    speaker_id: str = Field(
        ...,
        min_length=1,
        description="Alias of a configured speaker.",
    )
    text: str = Field(
        ...,
        min_length=1,
        description="Verbatim transcript for this turn.",
    )
    style_instructions: str | None = Field(
        default=None,
        description="Optional delivery style for this turn.",
    )


class GeminiTtsCommon(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    style_instructions: str | None = Field(
        default=None,
        max_length=4000,
        description=(
            "Optional style and delivery instructions prepended to the prompt. Controls "
            "expressiveness, accent, pace, tone, and emotional expression using natural "
            "language. Use this to separate style control from the text content. Examples: "
            "'Speak warmly and slowly', 'Read this as a dramatic newscast', 'Use a British "
            "accent with a cheerful tone', 'Whisper mysteriously'."
        ),
    )
    voice: GeminiTtsVoice = Field(
        default="Kore",
        description=(
            "Voice preset for single-speaker synthesis. 30 distinct voices are available. "
            "Ignored when speakers is set. Popular choices: Kore (strong, firm female), Puck "
            "(upbeat, lively male), Charon (calm, professional male), Zephyr (bright, clear "
            "female), Aoede (warm, melodic female)."
        ),
    )
    language_code: GeminiTtsLanguage | None = Field(
        default=None,
        description=(
            "Language for multilingual synthesis. When set, steers the model to speak in the "
            "specified language. Supports 24 GA languages and 60+ Preview languages. If not "
            "set, the model auto-detects the language from the text."
        ),
    )
    temperature: float = Field(
        default=1,
        ge=0,
        le=2,
        description=(
            "Controls the randomness of the speech output. Higher values produce more creative "
            "and varied delivery, while lower values make the output more predictable and "
            "focused."
        ),
    )
    output_format: Literal["wav", "mp3", "ogg_opus"] = Field(
        default="mp3",
        description=(
            "Audio output format. mp3: compressed, small file size (recommended). wav: "
            "uncompressed PCM wrapped in WAV (24 kHz, 16-bit mono). ogg_opus: Ogg container "
            "with Opus codec, good quality-to-size ratio."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Check input content for safety. Disabling requires account authorization.",
    )

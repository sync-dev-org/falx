from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from falx.models.gemini_tts_common import GeminiTtsCommon, GeminiTtsLanguage, GeminiTtsSpeaker


class Gemini31FlashTtsConfig(GeminiTtsCommon):
    app_id: Literal["fal-ai/gemini-3.1-flash-tts"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description=(
            "The text to convert to speech. Gemini 3.1 Flash TTS supports natural-language "
            "prompting for style, pace, accent, and emotional expression — include delivery "
            "instructions inline with the text (e.g. 'Say cheerfully: Have a wonderful day!'). "
            "Supports expressive audio tags like [sigh], [laughing], [whispering], [short "
            "pause] for fine-grained control over delivery. For multi-speaker synthesis, prefix"
            " lines with speaker aliases defined in the speakers field (e.g. 'Alice: "
            "Hello!\\nBob: Hi!')."
        ),
    )
    speakers: (
        Annotated[list[GeminiTtsSpeaker], Field(min_length=2, max_length=10)]
        | Annotated[list[GeminiTtsSpeaker], Field(min_length=0, max_length=0)]
        | None
    ) = Field(
        default=None,
        description=(
            "Multi-speaker voice configuration. When set, enables multi-speaker synthesis where"
            " different parts of the text are spoken by different voices. Each speaker needs a "
            "voice and a speaker_id (alias) that matches prefixes in the prompt."
        ),
    )
    language_code: GeminiTtsLanguage | None = Field(
        default=None,
        description=(
            "Language for multilingual synthesis. When set, steers the model to speak in the "
            "specified language. If not set, the model auto-detects the language from the text."
        ),
    )

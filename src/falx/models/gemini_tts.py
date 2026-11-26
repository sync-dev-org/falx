from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.gemini_tts_common import GeminiTtsCommon, GeminiTtsSpeaker


class GeminiTtsConfig(GeminiTtsCommon):
    app_id: Literal["fal-ai/gemini-tts"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description=(
            "The text to convert to speech. Gemini TTS supports natural-language prompting for "
            "style, pace, accent, and emotional expression — include delivery instructions "
            "inline with the text (e.g. 'Say cheerfully: Have a wonderful day!'). For "
            "multi-speaker synthesis, prefix lines with speaker aliases defined in the speakers"
            " field (e.g. 'Alice: Hello!\\nBob: Hi!'). Supports inline pace/style markers like "
            "[slowly], [whispering], [excited], [extremely fast]."
        ),
    )
    model: Literal["gemini-2.5-flash-tts", "gemini-2.5-pro-tts"] = Field(
        default="gemini-2.5-flash-tts",
        description=(
            "Which Gemini TTS model to use. gemini-2.5-flash-tts: low latency, cost-efficient "
            "for everyday applications (recommended). gemini-2.5-pro-tts: highest quality, best"
            " for structured workflows like podcasts, audiobooks, and customer support."
        ),
    )
    speakers: list[GeminiTtsSpeaker] | None = Field(
        default=None,
        min_length=2,
        max_length=10,
        description=(
            "Multi-speaker voice configuration. When set, enables multi-speaker synthesis where"
            " different parts of the text are spoken by different voices. Each speaker needs a "
            "voice and a speaker_id (alias) that matches prefixes in the prompt. Requires "
            "gemini-2.5-pro-tts or gemini-2.5-flash-tts model. Not supported with "
            "gemini-2.5-flash-lite-preview-tts."
        ),
    )

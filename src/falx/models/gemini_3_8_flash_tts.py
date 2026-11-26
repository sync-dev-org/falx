from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.gemini_tts_common import Gemini38SpeechTurn, Gemini38TtsSpeaker, GeminiTtsVoice


class Gemini38FlashTtsConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None
    schema_example_parameters: ClassVar[dict[str, Any]] = {"prompt": "<your prompt here>"}

    app_id: Literal["google/gemini-3.8-flash-tts"]
    prompt: str | None = Field(
        default=None,
        description=(
            "Verbatim text for single-speaker speech. Put delivery directions in "
            "style_instructions; inline vocal events may use <laugh> or <sigh>. For dialogue, "
            "omit prompt and provide speakers and turns instead. The provider limits the "
            "complete input to 8,192 tokens."
        ),
    )
    style_instructions: str | None = Field(
        default=None,
        description=(
            "Delivery style, separate from the spoken transcript. Applies to all turns unless "
            "overridden."
        ),
    )
    voice: GeminiTtsVoice = Field(
        default="Kore",
        description="Prebuilt voice for single-speaker speech.",
    )
    speakers: list[Gemini38TtsSpeaker] | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        description=(
            "Exactly two distinct speaker aliases and their prebuilt voices for dialogue."
        ),
    )
    turns: list[Gemini38SpeechTurn] | None = Field(
        default=None,
        min_length=1,
        description="Ordered dialogue turns, each identifying a configured speaker.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

    @model_validator(mode="after")
    def validate_speech_input(self) -> Self:
        if self.speakers is None and self.turns is None:
            if self.prompt is None:
                raise ValueError("prompt or speakers and turns are required")
            return self
        if self.speakers is None or self.turns is None:
            raise ValueError("speakers and turns must be provided together")
        aliases = {speaker.speaker_id for speaker in self.speakers}
        if len(aliases) != len(self.speakers):
            raise ValueError("speakers must have distinct speaker_id aliases")
        if any(turn.speaker_id not in aliases for turn in self.turns):
            raise ValueError("each turn speaker_id must identify a configured speaker")
        return self

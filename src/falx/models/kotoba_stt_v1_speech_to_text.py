from __future__ import annotations

from typing import Annotated, ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class KotobaSttV1SpeechToTextConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["kotoba-technologies/kotoba-stt/v1/speech-to-text"]
    audio_url: str = Field(
        ...,
        description=(
            "Speech to transcribe: an https:// URL on fal's CDN (Playground uploads and "
            "microphone recordings) or a base64 data: URI. Up to 2 minutes."
        ),
    )
    language: Literal["ja", "en", "ko", "zh", "es", "zh-hk", "zh-tw", "auto"] = Field(
        ...,
        description="Language spoken in the audio.",
    )
    with_timestamps: bool = Field(
        default=False,
        description="Return `words` with start and end times for each word.",
    )
    diarization: bool = Field(
        default=False,
        description=(
            "Attribute words to speakers (`speaker_id` on each word; models with speaker "
            "tokens only). Word times are null unless `with_timestamps` is also set."
        ),
    )
    keywords: list[Annotated[str, Field(max_length=64)]] | None = Field(
        default=None,
        max_length=1000,
        description=(
            "Up to 1000 terms of at most 64 characters, such as names or product words, "
            "whose spelling the transcript should prefer."
        ),
    )
    kana: bool = Field(
        default=False,
        description="Write personal and place names in katakana (Japanese).",
    )

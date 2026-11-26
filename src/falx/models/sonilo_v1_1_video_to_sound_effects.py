from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from falx.models import BaseFalConfig


class SoniloV11SfxSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: float = Field(
        default=0.0,
        ge=0,
        description=(
            "Segment start time in seconds (from video start). The FIRST segment's "
            "start must be 0."
        ),
    )
    end: float = Field(
        default=0.0,
        ge=0,
        description=(
            "Segment end time in seconds. Must equal the next segment's start "
            "(contiguous; no gaps/overlaps); the last segment's end must be <= the "
            "video duration."
        ),
    )
    prompt: str = Field(
        default="",
        description="SFX / foley description for this segment.",
    )


class SoniloV11VideoToSoundEffectsConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["sonilo/v1.1/video-to-sound-effects"]
    video_url: str = Field(
        ...,
        description=(
            "The video to add sound to (public URL, or upload a file). The generated "
            "audio matches the video's length."
        ),
    )
    prompt: str | None = Field(
        default=None,
        description=(
            "Optional. Describe the kind of sound you want; it steers the generated "
            "audio for every scene. Leave empty to caption the video automatically."
        ),
    )
    segments: list[SoniloV11SfxSegment] | None = Field(
        default=None,
        description=(
            "Optional. Split the video into time ranges, each with its own sound "
            "description. Leave empty to split into scenes automatically."
        ),
    )
    audio_format: Literal["wav", "mp3", "aac", "flac"] = Field(
        default="aac",
        description=(
            "Format of the returned audio file: aac (default), mp3, wav, or flac. "
            "(The video with sound is always AAC.)"
        ),
    )

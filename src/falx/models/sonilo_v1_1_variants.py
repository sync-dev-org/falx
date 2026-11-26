from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.sonilo_v1_1_video_to_sound_effects import SoniloV11VideoToSoundEffectsConfig


class SoniloV11TextToMusicConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["sonilo/v1.1/text-to-music"]
    prompt: str = Field(
        ...,
        description="Text prompt describing the music to generate.",
    )
    duration: int = Field(
        default=90,
        ge=1,
        le=600,
        description=(
            "Requested output duration in seconds (max 600). Also used for billing "
            "(one billable unit per second per sample, rounded up; each sample under "
            "10s bills as 10s)."
        ),
    )
    num_samples: int = Field(
        default=1,
        ge=1,
        le=3,
        description="How many distinct music tracks to generate.",
    )


class SoniloV11TextToSoundEffectsConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["sonilo/v1.1/text-to-sound-effects"]
    prompt: str = Field(
        ...,
        description="Describe the sound you want to create.",
    )
    duration: float = Field(
        default=8.0,
        ge=0.5,
        le=180,
        description="How long the audio should be, in seconds (0.5 to 180).",
    )
    audio_format: Literal["wav", "mp3", "aac", "flac"] = Field(
        default="aac",
        description="Audio file format: aac (default), mp3, wav, or flac.",
    )


class SoniloV11VideoToMusicConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["sonilo/v1.1/video-to-music"]
    video_url: str = Field(
        ...,
        description="Public http(s) URL of the source video to score.",
    )
    num_samples: int = Field(
        default=1,
        ge=1,
        le=3,
        description="How many distinct music tracks to generate for the video.",
    )
    prompt: str | None = Field(
        default=None,
        description=(
            "Optional text prompt steering the music style. If omitted, a prompt "
            "is generated automatically from the video."
        ),
    )
    prompt_influence: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description="Turn it up to match the text prompt",
    )
    start_offset: float | None = Field(
        default=None,
        ge=0,
        le=600,
        description=(
            "Optional. Start scoring from this offset (seconds) into the video. "
            "Requires Start Offset + Duration <= Video Duration."
        ),
    )
    duration: float | None = Field(
        default=None,
        ge=1,
        le=600,
        description=(
            "Optional. Length (seconds) of the video segment to score. When set, "
            "scores a segment of this length starting at Start Offset (or from the "
            "beginning if Start Offset is unset). Defaults (None) to the rest of "
            "the video: the whole video when Start Offset is unset, or from Start "
            "Offset to the end when it is set."
        ),
    )


class SoniloV11VideoToVideoMusicConfig(SoniloV11VideoToMusicConfig):
    app_id: Literal["sonilo/v1.1/video-to-video-music"]
    keep_speech_vocal: bool = Field(
        default=False,
        description=(
            "Keep the original video's speech/vocals. When on, the source audio is "
            "separated (music source separation), and only the isolated vocals are "
            "blended over the generated music with automatic ducking (the music dips "
            "under speech). When off (default), the original soundtrack is dropped "
            "and the video carries only the generated music."
        ),
    )
    num_samples: int = Field(
        default=1,
        ge=1,
        le=3,
        description="How many distinct scored videos to generate.",
    )
    duration: float | None = Field(
        default=None,
        ge=1,
        le=600,
        description=(
            "Optional. Length (seconds) of the video segment to score. When set, "
            "scores a segment of this length starting at Start Offset (or from the "
            "beginning if Start Offset is unset). Defaults (None) to the rest of the video."
        ),
    )


class SoniloV11VideoToVideoSoundEffectsConfig(SoniloV11VideoToSoundEffectsConfig):
    app_id: Literal["sonilo/v1.1/video-to-video-sound-effects"]
    keep_speech_vocal: bool = Field(
        default=False,
        description=(
            "Keep the original video's speech/vocals. When on, the source audio is "
            "separated (music source separation) and the isolated vocals are kept as "
            "recorded, with the generated sound mixed in at a level matched to the "
            "voice; the rest of the original soundtrack (music, ambience) is dropped. "
            "Applies to the returned audio and video. When off (default), the result "
            "carries only the generated sound."
        ),
    )

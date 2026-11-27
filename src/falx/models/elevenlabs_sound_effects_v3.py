from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class ElevenLabsSoundEffectsV3Config(BaseFalConfig):
    app_id: Literal["elevenlabs/sound-effects/v3"]
    text: str = Field(
        ...,
        max_length=450,
        description="The text describing the sound effect to generate",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Check input content for safety. Disabling requires account authorization.",
    )
    duration_seconds: float | None = Field(
        default=None,
        ge=0.5,
        le=30,
        description=(
            "Duration in seconds (0.5-30). If None, optimal duration will be determined "
            "from prompt."
        ),
    )
    prompt_influence: float = Field(
        default=0.3,
        ge=0,
        le=1,
        description="How closely to follow the prompt (0-1). Higher values mean less variation.",
    )
    output_format: Literal[
        "mp3_22050_32",
        "mp3_44100_32",
        "mp3_44100_64",
        "mp3_44100_96",
        "mp3_44100_128",
        "mp3_44100_192",
        "pcm_8000",
        "pcm_16000",
        "pcm_22050",
        "pcm_24000",
        "pcm_44100",
        "pcm_48000",
        "ulaw_8000",
        "alaw_8000",
        "opus_48000_32",
        "opus_48000_64",
        "opus_48000_96",
        "opus_48000_128",
        "opus_48000_192",
    ] = Field(
        default="mp3_44100_128",
        description=(
            "Output format of the generated audio. Formatted as codec_sample_rate_bitrate."
        ),
    )
    loop: bool = Field(
        default=False,
        description="Whether to create a sound effect that loops smoothly.",
    )

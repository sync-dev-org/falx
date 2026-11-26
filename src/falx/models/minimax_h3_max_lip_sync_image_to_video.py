from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MinimaxH3MaxLipSyncImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max/lip-sync/image-to-video"]
    image_url: str = Field(
        ...,
        description="Image to animate. The aspect ratio must be between 0.4 and 2.5.",
    )
    audio_url: str = Field(
        ...,
        description=(
            "Audio to synchronize the mouth movements to, at least 5 seconds long. "
            "Supports up to 15 minutes. The output video matches the supplied "
            "audio duration."
        ),
    )
    resolution: Literal["480P", "768P", "1080P", "2K"] = Field(
        default="768P",
        description="Output resolution. Uses the supported aspect ratio nearest the image.",
    )
    enable_transcription: bool = Field(
        default=True,
        description=(
            "Transcribe the supplied audio to guide lip synchronization. Turn this "
            "off if the audio has a lot of non-word sound, such as music, singing, "
            "laughter or noise, which the transcript may turn into words that were "
            "never spoken."
        ),
    )
    seed: int | None = Field(
        default=None,
        ge=0,
        le=2_147_483_647,
        description="Random seed; selected randomly if omitted.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Enable content safety checks.",
    )

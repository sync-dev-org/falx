from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

GrokImagineVideoV15AspectRatio = Literal[
    "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "21:9", "5:2"
]
GrokImagineVideoV15Resolution = Literal["480p", "720p", "1080p"]


class GrokImagineVideoV15TextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["xai/grok-imagine-video/v1.5/text-to-video"]
    prompt: str = Field(
        ...,
        max_length=4096,
        description="Text description of the desired video.",
    )
    duration: int = Field(
        default=6,
        ge=1,
        le=15,
        description="Video duration in seconds.",
    )
    resolution: GrokImagineVideoV15Resolution = Field(
        default="720p",
        description="Resolution of the output video.",
    )
    aspect_ratio: GrokImagineVideoV15AspectRatio = Field(
        default="16:9",
        description="Aspect ratio of the generated video.",
    )
    generate_audio: bool | None = Field(
        default=None,
        description=(
            "Whether to generate audio. When unset, xAI's default applies (audio included)."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

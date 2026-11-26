from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from falx.models import BaseFalConfig
from falx.models.grok_imagine_video_v1_5_text_to_video import GrokImagineVideoV15Resolution


class GrokImagineVideoV15LiteBaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

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


class GrokImagineVideoV15LiteKeyframe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_url: str = Field(
        ...,
        description="URL of the image to pin at `timestamp`.",
    )
    timestamp: float = Field(
        ...,
        gt=0,
        description=(
            "Time in seconds at which the image is pinned. "
            "Must be strictly between 0 and the video duration."
        ),
    )

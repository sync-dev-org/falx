from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.grok_imagine_video_v1_5_text_to_video import (
    GrokImagineVideoV15Resolution,
)


class GrokImagineVideoV15ImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["xai/grok-imagine-video/v1.5/image-to-video"]
    prompt: str = Field(
        ...,
        max_length=4096,
        description="Text description of desired changes or motion in the video.",
    )
    image_url: str = Field(
        ...,
        description="URL of the input image for video generation.",
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

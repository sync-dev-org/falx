from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.grok_imagine_video_v1_5_text_to_video import (
    GrokImagineVideoV15AspectRatio,
)

GrokImagineVideoV15ReferenceResolution = Literal["480p", "720p"]


class GrokImagineVideoV15ReferenceToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["xai/grok-imagine-video/v1.5/reference-to-video"]
    prompt: str = Field(
        ...,
        max_length=4096,
        description=(
            "Text prompt describing the video. Tag references as <IMAGE_0>, <IMAGE_1>, etc."
        ),
    )
    reference_image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=7,
        description=(
            "One or more reference image URLs to guide the video generation as style and "
            "content references. Reference in prompt as <IMAGE_0>, <IMAGE_1>, etc. "
            "Maximum 7 images."
        ),
    )
    duration: int = Field(
        default=8,
        ge=1,
        le=15,
        description="Video duration in seconds.",
    )
    resolution: GrokImagineVideoV15ReferenceResolution = Field(
        default="480p",
        description="Resolution of the output video.",
    )
    aspect_ratio: GrokImagineVideoV15AspectRatio = Field(
        default="16:9",
        description="Aspect ratio of the generated video.",
    )

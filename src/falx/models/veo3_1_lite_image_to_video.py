from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.veo3_1_common import (
    VEO31_AUTO_ASPECT_RATIO_DESCRIPTION,
    VEO31_RESOLUTION_DESCRIPTION,
    Veo31AutoAspectRatio,
)
from falx.models.veo3_1_image_to_video import Veo31ImageToVideoConfig


class Veo31LiteImageToVideoConfig(Veo31ImageToVideoConfig):
    app_id: Literal["fal-ai/veo3.1/lite/image-to-video"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description="The text prompt describing how the image should be animated",
    )
    aspect_ratio: Veo31AutoAspectRatio = Field(
        default="auto",
        description=VEO31_AUTO_ASPECT_RATIO_DESCRIPTION,
    )
    resolution: Literal["720p", "1080p"] = Field(
        default="720p",
        description=VEO31_RESOLUTION_DESCRIPTION,
    )
    image_url: str = Field(
        ...,
        description=(
            "URL of the input image to animate. Should be 720p or higher resolution "
            "in 16:9 or 9:16 aspect ratio."
        ),
    )

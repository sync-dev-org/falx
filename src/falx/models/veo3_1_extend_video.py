from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.veo3_1_common import (
    VEO31_AUTO_ASPECT_RATIO_DESCRIPTION,
    VEO31_DURATION_DESCRIPTION,
    VEO31_RESOLUTION_DESCRIPTION,
    Veo31AutoAspectRatio,
)
from falx.models.veo3_1_text_to_video import Veo31TextToVideoConfig


class Veo31ExtendVideoConfig(Veo31TextToVideoConfig):
    app_id: Literal["fal-ai/veo3.1/extend-video", "fal-ai/veo3.1/fast/extend-video"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description="The text prompt describing how the video should be extended",
    )
    aspect_ratio: Veo31AutoAspectRatio = Field(
        default="auto",
        description=VEO31_AUTO_ASPECT_RATIO_DESCRIPTION,
    )
    duration: Literal["7s"] = Field(
        default="7s",
        description=VEO31_DURATION_DESCRIPTION,
    )
    resolution: Literal["720p"] = Field(
        default="720p",
        description=VEO31_RESOLUTION_DESCRIPTION,
    )
    auto_fix: bool = Field(
        default=False,
        description=(
            "Whether to automatically attempt to fix prompts that fail content policy "
            "or other validation checks by rewriting them."
        ),
    )
    video_url: str = Field(
        ...,
        description=(
            "URL of the video to extend. The video should be 720p or 1080p resolution "
            "in 16:9 or 9:16 aspect ratio."
        ),
    )

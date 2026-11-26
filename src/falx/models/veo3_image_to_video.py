from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.veo3_common import Veo3Common


class Veo3ImageToVideoConfig(Veo3Common):
    app_id: Literal["fal-ai/veo3/image-to-video", "fal-ai/veo3/fast/image-to-video"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description="The text prompt describing how the image should be animated",
    )
    aspect_ratio: Literal["auto", "16:9", "9:16"] = Field(
        default="auto",
        description="The aspect ratio of the generated video.",
    )
    auto_fix: bool = Field(
        default=False,
        description=(
            "Whether to automatically attempt to fix prompts that fail content policy "
            "or other validation checks by rewriting them."
        ),
    )
    image_url: str = Field(
        ...,
        description=(
            "URL of the input image to animate. Should be 720p or higher resolution "
            "in 16:9 or 9:16 aspect ratio. If the image is not in 16:9 or 9:16 aspect "
            "ratio, it will be cropped to fit."
        ),
    )

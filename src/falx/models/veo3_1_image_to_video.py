from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.veo3_1_common import (
    VEO31_AUTO_ASPECT_RATIO_DESCRIPTION,
    VEO31_DURATION_DESCRIPTION,
    VEO31_RESOLUTION_DESCRIPTION,
    VEO31_SAFETY_TOLERANCE_DESCRIPTION,
    Veo31AutoAspectRatio,
    Veo31Duration,
    Veo31Resolution,
    Veo31SafetyTolerance,
)


class Veo31ImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["fal-ai/veo3.1/image-to-video"]
    prompt: str = Field(
        ...,
        description="The text prompt describing the video you want to generate.",
    )
    aspect_ratio: Veo31AutoAspectRatio = Field(
        default="auto",
        description=VEO31_AUTO_ASPECT_RATIO_DESCRIPTION,
    )
    duration: Veo31Duration = Field(
        default="8s",
        description=VEO31_DURATION_DESCRIPTION,
    )
    negative_prompt: str | None = Field(
        default=None,
        description="A negative prompt to guide the video generation.",
    )
    resolution: Veo31Resolution = Field(
        default="720p",
        description=VEO31_RESOLUTION_DESCRIPTION,
    )
    generate_audio: bool = Field(
        default=True,
        description="Whether to generate audio for the video.",
    )
    seed: int | None = Field(
        default=None,
        description="The seed for the random number generator.",
    )
    auto_fix: bool = Field(
        default=False,
        description=(
            "Whether to automatically attempt to fix prompts that fail content policy "
            "or other validation checks by rewriting them."
        ),
    )
    safety_tolerance: Veo31SafetyTolerance = Field(
        default="4",
        description=VEO31_SAFETY_TOLERANCE_DESCRIPTION,
    )
    image_url: str = Field(
        ...,
        description=(
            "URL of the input image to animate. Should be 720p or higher resolution "
            "in 16:9 or 9:16 aspect ratio."
        ),
    )

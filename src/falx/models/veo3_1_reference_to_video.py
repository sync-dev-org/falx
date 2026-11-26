from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.veo3_1_common import (
    VEO31_ASPECT_RATIO_DESCRIPTION,
    VEO31_RESOLUTION_DESCRIPTION,
    VEO31_SAFETY_TOLERANCE_DESCRIPTION,
    Veo31AspectRatio,
    Veo31Resolution,
    Veo31SafetyTolerance,
)


class Veo31ReferenceToVideoConfig(BaseFalConfig):
    app_id: Literal["fal-ai/veo3.1/reference-to-video"]
    prompt: str = Field(
        ...,
        description="The text prompt describing the video you want to generate.",
    )
    aspect_ratio: Veo31AspectRatio = Field(
        default="16:9",
        description=VEO31_ASPECT_RATIO_DESCRIPTION,
    )
    duration: str = Field(
        default="8s",
        description="The duration of the generated video.",
    )
    resolution: Veo31Resolution = Field(
        default="720p",
        description=VEO31_RESOLUTION_DESCRIPTION,
    )
    generate_audio: bool = Field(
        default=True,
        description="Whether to generate audio for the video.",
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
    image_urls: list[str] = Field(
        ...,
        description="URLs of the reference images to use for consistent subject appearance.",
    )

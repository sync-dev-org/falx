from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.gemini_omni_flash_v1_1_common import (
    GeminiOmniFlashV11AspectRatio,
    GeminiOmniFlashV11Resolution,
)


class GeminiOmniFlashV11ImageToVideoConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/v1.1/image-to-video"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description=(
            "The text prompt describing how the first image should be animated or "
            "interpolated into the optional end image."
        ),
    )
    image_url: str = Field(..., description="URL of the first frame to animate.")
    end_image_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of the end frame. When provided, the model interpolates "
            "between the two images in their listed order."
        ),
    )
    aspect_ratio: GeminiOmniFlashV11AspectRatio = Field(
        default="16:9",
        description="The aspect ratio of the generated video.",
    )
    resolution: GeminiOmniFlashV11Resolution = Field(
        default="720p",
        description="The resolution of the generated video.",
    )
    duration: int = Field(
        default=8,
        ge=3,
        le=10,
        description="The duration of the generated video, in seconds.",
    )

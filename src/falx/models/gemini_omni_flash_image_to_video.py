from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.gemini_omni_flash_common import (
    GeminiOmniFlashAspectRatio,
)


class GeminiOmniFlashImageToVideoConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/image-to-video"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description="The text prompt describing how the image should be animated.",
    )
    image_url: str = Field(
        ...,
        description="URL of the input image to animate.",
    )
    aspect_ratio: GeminiOmniFlashAspectRatio = Field(
        default="16:9",
        description="The aspect ratio of the generated video.",
    )
    duration: int = Field(
        default=8,
        ge=3,
        le=10,
        description="The duration of the generated video, in seconds.",
    )

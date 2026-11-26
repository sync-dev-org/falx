from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.gemini_omni_flash_v1_1_common import (
    GeminiOmniFlashV11AspectRatio,
    GeminiOmniFlashV11Resolution,
)


class GeminiOmniFlashV11TextToVideoConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/v1.1/text-to-video"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description="The text prompt describing the video you want to generate.",
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

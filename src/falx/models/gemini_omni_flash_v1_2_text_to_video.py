from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.gemini_omni_flash_v1_2_common import (
    GeminiOmniFlashV12AspectRatio,
    GeminiOmniFlashV12Resolution,
)


class GeminiOmniFlashV12TextToVideoConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/v1.2/text-to-video"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description="The text prompt describing the video you want to generate.",
    )
    aspect_ratio: GeminiOmniFlashV12AspectRatio = Field(
        default="16:9",
        description="The aspect ratio of the generated video.",
    )
    resolution: GeminiOmniFlashV12Resolution = Field(
        default="720p",
        description="The resolution of the generated video.",
    )
    duration: int = Field(
        default=8,
        ge=3,
        le=15,
        description="The duration of the generated video, in seconds.",
    )

from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.gemini_omni_flash_v1_1_common import (
    GeminiOmniFlashV11AspectRatio,
    GeminiOmniFlashV11Resolution,
)


class GeminiOmniFlashV11ReferenceToVideoConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/v1.1/reference-to-video"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description=(
            "The text prompt describing the video. Reference media is sent in list order "
            "before the prompt."
        ),
    )
    image_urls: list[str] | None = Field(
        default=None,
        max_length=10,
        description="URLs of reference images to incorporate into the video.",
    )
    reference_video_urls: list[str] | None = Field(
        default=None,
        max_length=3,
        description=(
            "URLs of up to three reference videos. Each video must be at most three seconds long."
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

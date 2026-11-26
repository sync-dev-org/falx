from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.gemini_omni_flash_common import (
    GeminiOmniFlashAspectRatio,
)


class GeminiOmniFlashReferenceToVideoConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/reference-to-video"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description=(
            "The text prompt describing the video. You can bind reference images to roles "
            "inline using tags like ``<IMAGE_REF_0>`` (see the Omni Flash prompt guide)."
        ),
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="URLs of the reference images to incorporate into the video.",
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

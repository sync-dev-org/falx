from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.gemini_omni_flash_v1_2_common import (
    GeminiOmniFlashV12AspectRatio,
    GeminiOmniFlashV12Resolution,
)


class GeminiOmniFlashV12ImageToVideoConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/v1.2/image-to-video"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description=(
            "The text prompt describing how the first image should be animated or "
            "interpolated into the optional end image."
        ),
    )
    image_url: str = Field(
        ...,
        description="URL of the first frame to animate.",
    )
    end_image_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of the end frame. When provided, the model interpolates between the "
            "two images in their listed order and the duration is capped at 10 seconds."
        ),
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
        description=(
            "The duration of the generated video, in seconds. At most 10 seconds when an end "
            "image is provided."
        ),
    )

    @model_validator(mode="after")
    def validate_interpolation_duration(self) -> GeminiOmniFlashV12ImageToVideoConfig:
        if self.end_image_url is not None and self.duration > 10:
            raise ValueError("duration must be at most 10 seconds when end_image_url is provided")
        return self

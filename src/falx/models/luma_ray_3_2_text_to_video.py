from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.luma_ray_3_2_common import (
    LUMA_RAY_32_ASPECT_RATIO_DESCRIPTION,
    LUMA_RAY_32_DURATION_DESCRIPTION,
    LUMA_RAY_32_RESOLUTION_DESCRIPTION,
    LumaRay32AspectRatio,
    LumaRay32Duration,
    LumaRay32Resolution,
    validate_hdr_options,
)


class LumaRay32TextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["luma/agent/ray/v3.2/text-to-video"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=6000,
        description="Text prompt describing the video to generate.",
    )
    aspect_ratio: LumaRay32AspectRatio = Field(
        default="16:9",
        description=LUMA_RAY_32_ASPECT_RATIO_DESCRIPTION,
    )
    resolution: LumaRay32Resolution = Field(
        default="540p",
        description=LUMA_RAY_32_RESOLUTION_DESCRIPTION,
    )
    duration: LumaRay32Duration = Field(
        default="5s",
        description=LUMA_RAY_32_DURATION_DESCRIPTION,
    )
    loop: bool = Field(
        default=False,
        description=(
            "Generate a seamless loop. Only valid for 5s, standard-dynamic-range "
            "generations without an end frame."
        ),
    )
    hdr: bool = Field(
        default=False,
        description=(
            "Generate an HDR-encoded MP4. Requires HDR access on the account and a "
            "resolution of 720p or 1080p; not supported with 10s or loop."
        ),
    )
    exr_export: bool = Field(
        default=False,
        description="Also export an EXR file alongside the MP4. Requires hdr=true and HDR access.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

    @model_validator(mode="after")
    def validate_text_to_video_options(self) -> Self:
        if self.loop and self.hdr:
            raise ValueError("loop cannot be combined with hdr")
        if self.loop and self.duration != "5s":
            raise ValueError("loop requires 5s duration")
        if self.hdr and self.duration == "10s":
            raise ValueError("hdr cannot be combined with 10s duration")
        validate_hdr_options(
            hdr=self.hdr,
            resolution=self.resolution,
            exr_export=self.exr_export,
        )
        return self

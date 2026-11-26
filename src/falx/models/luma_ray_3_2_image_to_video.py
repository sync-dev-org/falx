from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

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
    validate_keyframes,
)


class LumaRay32ImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None
    schema_example_parameters: ClassVar[dict[str, Any]] = {
        "image_url": "https://example.com/input",
    }

    app_id: Literal["luma/agent/ray/v3.2/image-to-video"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=6000,
        description="Text prompt describing the motion/scene to generate.",
    )
    image_url: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "URL of the image used as the first frame of the video. Provide either "
            "image_url (optionally with end_image_url) or keyframes."
        ),
    )
    end_image_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of an image used as the last frame. Cannot be combined with keyframes."
        ),
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
        description=(f"{LUMA_RAY_32_DURATION_DESCRIPTION} 10s requires multi-keyframe input."),
    )
    loop: bool = Field(
        default=False,
        description=(
            "Generate a seamless loop. Only valid for standard-dynamic-range "
            "generations without an end frame or keyframes."
        ),
    )
    hdr: bool = Field(
        default=False,
        description=(
            "Generate an HDR-encoded MP4. Requires HDR access on the account and a "
            "resolution of 720p or 1080p; not supported with loop."
        ),
    )
    exr_export: bool = Field(
        default=False,
        description="Also export an EXR file alongside the MP4. Requires hdr=true and HDR access.",
    )
    keyframes: list[str] | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description=(
            "Multi-keyframe image-to-video guide frames: 1-64 image URLs pinned at "
            "the positions given by keyframe_indexes."
        ),
    )
    keyframe_indexes: list[int] | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description=(
            "Output-frame positions where each keyframes[i] is anchored. "
            "Non-negative, unique, and the same length as keyframes."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

    @model_validator(mode="after")
    def validate_image_to_video_options(self) -> Self:
        validate_keyframes(keyframes=self.keyframes, keyframe_indexes=self.keyframe_indexes)

        has_image_anchor = self.image_url is not None
        has_end_anchor = self.end_image_url is not None
        has_keyframes = self.keyframes is not None

        if has_end_anchor and not has_image_anchor:
            raise ValueError("end_image_url requires image_url")
        if not has_image_anchor and not has_keyframes:
            raise ValueError("image_url or keyframes is required")
        if (has_image_anchor or has_end_anchor) and has_keyframes:
            raise ValueError("image_url/end_image_url cannot be combined with keyframes")
        if self.duration == "10s" and not has_keyframes:
            raise ValueError("10s requires keyframes")
        if self.loop and has_end_anchor:
            raise ValueError("loop cannot be combined with end_image_url")
        if self.loop and has_keyframes:
            raise ValueError("loop cannot be combined with keyframes")
        if self.loop and self.hdr:
            raise ValueError("loop cannot be combined with hdr")

        validate_hdr_options(
            hdr=self.hdr,
            resolution=self.resolution,
            exr_export=self.exr_export,
        )
        return self

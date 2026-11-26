from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.luma_ray_3_2_common import (
    LUMA_RAY_32_DURATION_DESCRIPTION,
    LUMA_RAY_32_RESOLUTION_DESCRIPTION,
    LumaRay32Duration,
    LumaRay32EditControls,
    LumaRay32EditStrength,
    LumaRay32Resolution,
    validate_hdr_options,
    validate_keyframes,
)


class LumaRay32VideoToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["luma/agent/ray/v3.2/video-to-video"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=6000,
        description="Text prompt describing how to edit the source video.",
    )
    video_url: str = Field(
        ...,
        min_length=1,
        description="URL of the source video to edit.",
    )
    user: str | None = Field(
        default=None,
        description=(
            "Optional opaque identifier for the end user making the request. "
            "Used only for abuse attribution; never interpreted by fal."
        ),
    )
    start_image_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of an image to use as the edited video's first frame. "
            "Cannot be combined with keyframes."
        ),
    )
    resolution: LumaRay32Resolution = Field(
        default="540p",
        description=LUMA_RAY_32_RESOLUTION_DESCRIPTION,
    )
    duration: LumaRay32Duration = Field(
        default="5s",
        description=LUMA_RAY_32_DURATION_DESCRIPTION,
    )
    edit_strength: LumaRay32EditStrength | None = Field(
        default=None,
        description=(
            "How closely the edit preserves the source video. Cannot be combined "
            "with auto_controls."
        ),
    )
    auto_controls: bool = Field(
        default=False,
        description=(
            "Let the model derive the edit conditioning schedule from the source video. "
            "Cannot be combined with edit_strength."
        ),
    )
    hdr: bool = Field(
        default=False,
        description=(
            "Generate an HDR-encoded MP4. Requires HDR access on the account and a "
            "resolution of 720p or 1080p."
        ),
    )
    exr_export: bool = Field(
        default=False,
        description="Also export an EXR file alongside the MP4. Requires hdr=true and HDR access.",
    )
    controls: LumaRay32EditControls | None = Field(
        default=None,
        description=(
            "Per-signal conditioning controls (pose, depth, normals, trajectory, face). "
            "Cannot be combined with auto_controls."
        ),
    )
    keyframes: list[str] | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description=(
            "Multi-keyframe edit guide frames: up to 64 image URLs pinned at the "
            "source-frame positions given by keyframe_indexes."
        ),
    )
    keyframe_indexes: list[int] | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description=(
            "Source-video frame positions where each keyframes[i] is anchored. "
            "Non-negative, unique, and the same length as keyframes."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

    @model_validator(mode="after")
    def validate_video_to_video_options(self) -> Self:
        validate_keyframes(keyframes=self.keyframes, keyframe_indexes=self.keyframe_indexes)
        if self.edit_strength is not None and self.auto_controls:
            raise ValueError("edit_strength cannot be combined with auto_controls")
        if self.controls is not None and self.auto_controls:
            raise ValueError("controls cannot be combined with auto_controls")
        if self.start_image_url is not None and self.keyframes is not None:
            raise ValueError("start_image_url cannot be combined with keyframes")
        validate_hdr_options(
            hdr=self.hdr,
            resolution=self.resolution,
            exr_export=self.exr_export,
        )
        return self

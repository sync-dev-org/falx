from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

LumaRay32AspectRatio = Literal["3:4", "4:3", "1:1", "9:16", "16:9", "21:9"]
LumaRay32Resolution = Literal["540p", "720p", "1080p"]
LumaRay32Duration = Literal["5s", "10s"]
LumaRay32EditStrength = Literal[
    "adhere_1",
    "adhere_2",
    "adhere_3",
    "flex_1",
    "flex_2",
    "flex_3",
    "reimagine_1",
    "reimagine_2",
    "reimagine_3",
]
LumaRay32PoseStrength = Literal["precise", "coarse"]

LUMA_RAY_32_ASPECT_RATIO_DESCRIPTION = (
    "Aspect ratio of the generated video. "
    "Allowed values: '3:4', '4:3', '1:1', '9:16', '16:9', '21:9' (string)."
)
LUMA_RAY_32_RESOLUTION_DESCRIPTION = (
    "Resolution of the generated video. Higher resolutions cost more. "
    "Allowed values: '540p', '720p', '1080p' (string)."
)
LUMA_RAY_32_DURATION_DESCRIPTION = (
    "Duration of the generated video. Allowed values: '5s', '10s' (string)."
)


class LumaRay32ReframeSourcePosition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x_norm: float = Field(
        ...,
        ge=-2,
        le=2,
        description="Left edge of the source rectangle as a fraction of output width.",
    )
    y_norm: float = Field(
        ...,
        ge=-2,
        le=2,
        description="Top edge of the source rectangle as a fraction of output height.",
    )
    w_norm: float = Field(
        ...,
        gt=0,
        le=2,
        description="Width of the source rectangle as a fraction of output width.",
    )
    h_norm: float = Field(
        ...,
        gt=0,
        le=2,
        description="Height of the source rectangle as a fraction of output height.",
    )


class LumaRay32EditPoseControl(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(
        default=True,
        description="Enable pose / skeleton conditioning for the edit.",
    )
    strength: LumaRay32PoseStrength | None = Field(
        default=None,
        description=(
            "Pose conditioning precision. 'precise' follows the source pose tightly; "
            "'coarse' allows more freedom. Leave unset for the default."
        ),
    )


class LumaRay32EditDepthControl(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(
        default=True,
        description="Enable depth / scene-geometry conditioning for the edit.",
    )
    blur: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Depth blur. Higher values allow more geometric freedom. Leave unset for the default."
        ),
    )


class LumaRay32EditNormalsControl(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(
        default=True,
        description="Enable surface-normals conditioning for the edit.",
    )
    augmentation: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Surface-normals augmentation. Higher values allow more reinterpretation "
            "of surface geometry. Leave unset for the default."
        ),
    )


class LumaRay32EditTrajectoryControl(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(
        default=True,
        description="Enable motion-trajectory conditioning for the edit.",
    )
    sparsity: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Motion-trajectory sparsity. Higher values use fewer motion anchors. "
            "Leave unset for the default."
        ),
    )


class LumaRay32EditFaceControl(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(
        default=True,
        description="Enable face-identity conditioning for the edit.",
    )


class LumaRay32EditControls(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pose: LumaRay32EditPoseControl | None = Field(
        default=None,
        description="Pose / skeleton conditioning.",
    )
    depth: LumaRay32EditDepthControl | None = Field(
        default=None,
        description="Depth / scene-geometry conditioning.",
    )
    normals: LumaRay32EditNormalsControl | None = Field(
        default=None,
        description="Surface-normals conditioning.",
    )
    trajectory: LumaRay32EditTrajectoryControl | None = Field(
        default=None,
        description="Motion-trajectory conditioning.",
    )
    face: LumaRay32EditFaceControl | None = Field(
        default=None,
        description="Face-identity conditioning.",
    )


def validate_hdr_options(
    *,
    hdr: bool,
    resolution: LumaRay32Resolution,
    exr_export: bool,
) -> None:
    if exr_export and not hdr:
        raise ValueError("exr_export requires hdr=true")
    if hdr and resolution == "540p":
        raise ValueError("hdr requires resolution 720p or 1080p")


def validate_keyframes(
    *,
    keyframes: list[str] | None,
    keyframe_indexes: list[int] | None,
) -> None:
    has_keyframes = keyframes is not None
    has_indexes = keyframe_indexes is not None
    if has_keyframes != has_indexes:
        raise ValueError("keyframes and keyframe_indexes must be provided together")
    if keyframes is None or keyframe_indexes is None:
        return
    if len(keyframes) != len(keyframe_indexes):
        raise ValueError("keyframes and keyframe_indexes must be the same length")
    if any(index < 0 for index in keyframe_indexes):
        raise ValueError("keyframe_indexes must be non-negative")
    if len(set(keyframe_indexes)) != len(keyframe_indexes):
        raise ValueError("keyframe_indexes must be unique")

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from falx.models import BaseFalConfig


class Ltx25AlphaGenConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["lightricks/ltx-2.5/alpha-gen"]
    video_url: str = Field(
        ...,
        description=(
            "URL of the source video, at most 200 MB and 3072 frames. Long side must not "
            "exceed 3840 pixels, short side 2160 pixels, and the ratio of long to short "
            "side must not exceed 32:9."
        ),
    )
    enable_safety_checker: bool = Field(default=True)


class Ltx25HdrConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["lightricks/ltx-2.5/hdr"]
    video_url: str = Field(..., description="URL of the source video.")
    enable_safety_checker: bool = Field(default=True)
    output_colorspace: Literal["acescg", "acescct", "srgb_linear", "aces2065-1"] = Field(
        default="acescg",
        description="Color space of the OpenEXR frames.",
    )


class Ltx25ReframeAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    anchor: Literal[
        "center",
        "top",
        "bottom",
        "left",
        "right",
        "top_left",
        "top_right",
        "bottom_left",
        "bottom_right",
    ] = Field(..., description="Fit and align the source video within the output frame.")


class Ltx25ReframeRectangle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float = Field(
        ...,
        ge=0,
        lt=1,
        description="Left edge as a fraction of output width.",
    )
    y: float = Field(
        ...,
        ge=0,
        lt=1,
        description="Top edge as a fraction of output height.",
    )
    width: float | None = Field(default=None, gt=0, le=1)
    height: float | None = Field(default=None, gt=0, le=1)


class Ltx25ReframeConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["lightricks/ltx-2.5/reframe"]
    video_url: str = Field(..., description="URL of the source video.")
    enable_safety_checker: bool = Field(default=True)
    aspect_ratio: Literal["1:1", "4:5", "5:4", "9:16", "16:9"] = Field(default="16:9")
    resolution: Literal[
        "720p",
        "1080p",
        "720x720",
        "1080x1080",
        "720x900",
        "1080x1350",
        "900x720",
        "1350x1080",
        "720x1280",
        "1080x1920",
        "1280x720",
        "1920x1080",
    ] = Field(
        default="1080p",
        description=(
            "Output tier or explicit frame dimensions. Explicit WxH dimensions must agree "
            "with aspect_ratio when both are explicitly provided."
        ),
    )
    placement: Ltx25ReframeAnchor | Ltx25ReframeRectangle | None = Field(
        default=None,
        description=(
            "Source placement. Omit to center at the largest size that fits. Rectangles "
            "preserve source aspect ratio, must fit in the frame, and cannot enlarge the "
            "source more than 2x."
        ),
    )

    @model_validator(mode="after")
    def validate_explicit_resolution_aspect_ratio(self) -> Ltx25ReframeConfig:
        if {"resolution", "aspect_ratio"} <= self.model_fields_set and "x" in self.resolution:
            width, height = (int(value) for value in self.resolution.split("x"))
            ratio_width, ratio_height = (int(value) for value in self.aspect_ratio.split(":"))
            if width * ratio_height != height * ratio_width:
                raise ValueError("resolution dimensions must agree with aspect_ratio")
        return self


class Ltx25UpscaleConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["lightricks/ltx-2.5/upscale"]
    video_url: str = Field(
        ...,
        description=(
            "URL of an H.264 or HEVC video, at most 200 MB. Input must have at least 2 "
            "frames and 1 fps, a short side of at least 480 pixels, a long side at most "
            "7680 and short side at most 4320 pixels. Maximum frames: 2401 for 1080p, 601 "
            "for 4k, 241 for 8k. Output keeps input audio in stereo and rounds input fps "
            "to an integer."
        ),
    )
    enable_safety_checker: bool = Field(default=True)
    resolution: Literal["1080p", "4k", "8k"] = Field(
        ...,
        description="Target output resolution.",
    )

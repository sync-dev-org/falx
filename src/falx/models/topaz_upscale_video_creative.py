from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazUpscaleVideoCreativeConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["topaz/upscale/video/creative"]
    enable_safety_checker: bool = Field(default=True)
    video_url: str = Field(
        ...,
        description="URL of the video to upscale",
    )
    prompt: str | None = Field(
        default=None,
        max_length=1024,
        description=(
            "Optional text prompt guiding the detail Astra 2 generates. When set, the input "
            "video is limited to 450 frames."
        ),
    )
    creativity: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description=(
            "How much new detail and texture Astra 2 invents. 0.0 stays faithful to the "
            "source, 1.0 is maximally creative."
        ),
    )
    realism: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Bias generated detail toward photorealism (0.0-1.0).",
    )
    sharp: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Output sharpness. 0.0 softens, 0.5 is neutral passthrough, 1.0 applies strong "
            "sharpening. Defaults to Topaz's neutral 0.5."
        ),
    )
    upscale_factor: float = Field(
        default=2,
        ge=1,
        le=4,
        description=(
            "Requested upscale factor (e.g. 2.0 doubles width and height). Note: Astra 2 "
            "snaps to its own supported output resolutions (typically 4K when upscaling) and "
            "may override the requested target. Billing is based on the delivered resolution."
        ),
    )
    target_fps: int | None = Field(
        default=None,
        ge=16,
        le=60,
        description=(
            "Target FPS for the output. Frame interpolation is enabled only when this differs "
            "from the source FPS."
        ),
    )
    H264_output: bool = Field(
        default=False,
        description="Whether to use H264 codec for output video. Default is H265.",
    )

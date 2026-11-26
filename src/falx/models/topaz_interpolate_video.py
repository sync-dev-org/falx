from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazInterpolateVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["topaz/interpolate/video"]
    video_url: str = Field(
        ...,
        description="URL of the video to retime / interpolate",
    )
    model: Literal["Apollo", "Chronos", "Aion"] = Field(
        default="Apollo",
        description=(
            "Frame interpolation model. Apollo is general-purpose; Chronos targets "
            "real-world motion; Aion handles extreme/complex motion."
        ),
    )
    target_fps: int = Field(
        default=60,
        ge=16,
        le=120,
        description="Target frames per second for the interpolated output.",
    )
    slowdown_factor: int = Field(
        default=1,
        ge=1,
        le=8,
        description=(
            "Slow-motion factor: 2 makes the output twice as long at the target FPS "
            "(2x slow motion), up to 8x. 1 keeps the original speed. The extra "
            "generated frames are billed like interpolated frames."
        ),
    )
    H264_output: bool = Field(
        default=False,
        description="Whether to use H264 codec for output video. Default is H265.",
    )
    enable_safety_checker: bool = Field(default=True)

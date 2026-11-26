from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazDeblurVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["topaz/deblur/video"]
    video_url: str = Field(
        ...,
        description="URL of the video to deblur (motion deblur, Themis 2)",
    )
    H264_output: bool = Field(
        default=False,
        description="Whether to use H264 codec for output video. Default is H265.",
    )
    enable_safety_checker: bool = Field(default=True)

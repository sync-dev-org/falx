from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.bria_video_common import BriaVideoOutputContainerAndCodec


class BriaVideoIncreaseResolutionConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["bria/video/increase-resolution"]
    video_url: str = Field(
        ...,
        description=(
            "Input video to increase resolution. "
            "Size should be less than 7680,4320 and duration less than 30s."
        ),
    )
    desired_increase: Literal["2", "4"] = Field(
        default="2",
        description="desired_increase factor. Options: 2x, 4x.",
    )
    preserve_audio: bool = Field(
        default=True,
        description="If true, audio will be preserved in the output video.",
    )
    output_container_and_codec: BriaVideoOutputContainerAndCodec = Field(
        default="webm_vp9",
        description=(
            "Output container and codec. Options: mp4_h265, mp4_h264, webm_vp9, mov_h265, "
            "mov_proresks, mkv_h265, mkv_h264, mkv_vp9, gif."
        ),
    )

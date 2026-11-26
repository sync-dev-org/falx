from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

BriaVideoOutputContainerAndCodec = Literal[
    "mp4_h265",
    "mp4_h264",
    "webm_vp9",
    "mov_h265",
    "mov_proresks",
    "mkv_h265",
    "mkv_h264",
    "mkv_vp9",
    "gif",
]


class BriaVideoBackgroundRemovalGreenScreenDespillConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["bria/video/background-removal/green-screen-despill"]
    video_url: str = Field(
        ...,
        description="Input video filmed on a green screen.",
    )
    spill_suppression: float = Field(
        default=1.0,
        ge=0,
        le=1,
        description=(
            "Strength of green-spill suppression. Higher values pull the green channel toward "
            "the red/blue average on green-dominant pixels, removing the green fringe around "
            "the subject. 0 disables it."
        ),
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

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.bria_video_common import BriaVideoOutputContainerAndCodec


class BriaVideoBackgroundRemovalConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["bria/video/background-removal"]
    video_url: str = Field(
        ...,
        description=(
            "Input video to remove background from. "
            "Size should be less than 4000x4000 and duration less than 30s."
        ),
    )
    background_color: Literal[
        "Transparent",
        "Black",
        "White",
        "Gray",
        "Red",
        "Green",
        "Blue",
        "Yellow",
        "Cyan",
        "Magenta",
        "Orange",
    ] = Field(
        default="Black",
        description=(
            "Background color. Options: Transparent, Black, White, Gray, Red, Green, Blue, "
            "Yellow, Cyan, Magenta, Orange."
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


class BriaVideoBackgroundRemovalV3Config(BriaVideoBackgroundRemovalConfig):
    app_id: Literal["bria/video/background-removal/v3"]
    video_url: str = Field(..., description="Input video to remove background from.")
    auto_zoom: bool = Field(
        default=False,
        description=(
            "If true, crop the output to the smallest rectangle "
            "the subject stays inside for the whole video."
        ),
    )

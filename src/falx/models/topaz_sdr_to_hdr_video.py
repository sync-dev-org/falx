from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazSdrToHdrVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["topaz/sdr-to-hdr/video"]
    enable_safety_checker: bool = Field(default=True)
    video_url: str = Field(
        ...,
        description="URL of the SDR video to convert to HDR",
    )
    output_format: Literal["mp4", "prores"] = Field(
        default="mp4",
        description=(
            "Output container/codec: mp4 delivers 10-bit H265 HDR10; prores delivers 10-bit "
            "ProRes 422 HQ in a .mov, Topaz's recommended format for grading and mastering "
            "workflows (much larger files)."
        ),
    )

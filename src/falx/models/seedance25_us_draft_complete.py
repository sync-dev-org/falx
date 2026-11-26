from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Seedance25UsDraftCompleteConfig(BaseFalConfig):
    app_id: Literal["bytedance/seedance-2.5/us/draft/complete"]
    draft_id: str = Field(
        ...,
        min_length=1,
        max_length=8192,
        description=(
            "The draft_id returned with draft enabled. Valid for 14 days and only for "
            "the original caller."
        ),
    )
    resolution: Literal["1080p", "4k"] = Field(
        default="1080p",
        description="Resolution of the completed video: 1080p or 4k.",
    )
    codec: Literal["auto", "H264", "H265"] = Field(
        default="auto",
        description=(
            "'auto' uses the default video codec; US backend output is kept unchanged. "
            "'H264' and 'H265' select H.264 and H.265 respectively."
        ),
    )
    output_format: Literal["mp4", "mov"] = Field(
        default="mp4",
        description=(
            "Output video format. 'mp4' is broadly compatible with browsers, mobile devices "
            "and media players. 'mov' targets professional post-production such as color "
            "grading, keying and compositing, but may not be supported by all players."
        ),
    )

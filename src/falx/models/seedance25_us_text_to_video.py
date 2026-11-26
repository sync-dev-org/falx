from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedance_us_common import Seedance25UsVideoConfig


class Seedance25UsTextToVideoConfig(Seedance25UsVideoConfig):
    app_id: Literal["bytedance/seedance-2.5/us/text-to-video"]
    prompt: str = Field(..., description="The text prompt used to generate the video")

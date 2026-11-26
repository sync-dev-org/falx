from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.heygen_video_common import HeygenVideoBaseConfig


class HeygenVideoTextToVideoConfig(HeygenVideoBaseConfig):
    app_id: Literal["heygen/heygen-video/text-to-video"]
    aspect_ratio: Literal["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(default="16:9")

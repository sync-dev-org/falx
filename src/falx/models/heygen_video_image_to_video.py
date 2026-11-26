from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.heygen_video_common import HeygenVideoBaseConfig


class HeygenVideoImageToVideoConfig(HeygenVideoBaseConfig):
    app_id: Literal["heygen/heygen-video/image-to-video"]
    image_url: str = Field(..., description="Image to use as the first frame")

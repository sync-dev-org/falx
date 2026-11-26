from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.heygen_video_common import HeygenVideoBaseConfig


class HeygenVideoReferenceToVideoConfig(HeygenVideoBaseConfig):
    app_id: Literal["heygen/heygen-video/reference-to-video"]
    reference_image_urls: list[str] = Field(default_factory=list, max_length=9)
    reference_video_urls: list[str] = Field(default_factory=list, max_length=3)
    reference_audio_urls: list[str] = Field(default_factory=list, max_length=3)
    aspect_ratio: Literal["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="adaptive",
    )

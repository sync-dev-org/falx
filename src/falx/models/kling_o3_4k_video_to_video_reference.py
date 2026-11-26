from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models.kling_o3_4k_video_to_video_edit import (
    KlingVideoO34kVideoToVideoEditConfig,
)
from falx.models.kling_o3_common import KlingO3Duration

KlingO34kVideoToVideoAspectRatio = Literal["auto", "16:9", "9:16", "1:1"]


class KlingVideoO34kVideoToVideoReferenceConfig(KlingVideoO34kVideoToVideoEditConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/4k/video-to-video/reference"]
    aspect_ratio: KlingO34kVideoToVideoAspectRatio = Field(
        default="auto",
        description="Aspect ratio.",
    )
    duration: KlingO3Duration | None = Field(
        default=None,
        description="Video duration in seconds (3-15s for reference video).",
    )

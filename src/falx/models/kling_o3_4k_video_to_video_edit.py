from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models.kling_o3_pro_video_to_video_edit import (
    KlingVideoO3ProVideoToVideoEditConfig,
)


class KlingVideoO34kVideoToVideoEditConfig(KlingVideoO3ProVideoToVideoEditConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/4k/video-to-video/edit"]
    video_url: str = Field(
        ...,
        description=(
            "Reference video URL. Only .mp4/.mov formats, 3-15s duration, "
            "720-3840px resolution, max 200MB."
        ),
    )

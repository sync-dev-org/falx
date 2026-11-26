from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models.kling_o3_4k_video_to_video_edit import (
    KlingVideoO34kVideoToVideoEditConfig,
)


class KlingVideoO3StandardVideoToVideoEditConfig(KlingVideoO34kVideoToVideoEditConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/standard/video-to-video/edit"]
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Disabling safety checks requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )

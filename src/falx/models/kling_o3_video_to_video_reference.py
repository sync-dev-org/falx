from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models.kling_o3_4k_video_to_video_reference import (
    KlingVideoO34kVideoToVideoReferenceConfig,
)


class KlingVideoO3VideoToVideoReferenceConfig(KlingVideoO34kVideoToVideoReferenceConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal[
        "fal-ai/kling-video/o3/standard/video-to-video/reference",
        "fal-ai/kling-video/o3/pro/video-to-video/reference",
    ]
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Disabling safety checks requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )

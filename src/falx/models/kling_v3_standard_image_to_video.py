from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models.kling_v3_pro_image_to_video import (
    KlingVideoV3ProImageToVideoConfig,
)


class KlingVideoV3StandardImageToVideoConfig(KlingVideoV3ProImageToVideoConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/v3/standard/image-to-video"]
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Disabling safety checks requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )

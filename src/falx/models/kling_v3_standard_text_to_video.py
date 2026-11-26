from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models.kling_v3_pro_text_to_video import (
    KlingVideoV3ProTextToVideoConfig,
)


class KlingVideoV3StandardTextToVideoConfig(KlingVideoV3ProTextToVideoConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/v3/standard/text-to-video"]
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Disabling safety checks requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )

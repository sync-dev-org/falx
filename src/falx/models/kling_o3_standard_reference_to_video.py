from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models.kling_o3_pro_reference_to_video import (
    KlingVideoO3ProReferenceToVideoConfig,
)


class KlingVideoO3StandardReferenceToVideoConfig(KlingVideoO3ProReferenceToVideoConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/standard/reference-to-video"]
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Disabling safety checks requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )

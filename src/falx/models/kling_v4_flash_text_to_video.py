from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.kling_v4_common import (
    KlingV4AspectRatio,
)


class KlingV4FlashTextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["kling/v4/flash/text-to-video"]
    prompt: str = Field(
        ...,
        max_length=26000,
        description="Text prompt for video generation.",
    )
    duration: int = Field(
        default=5,
        ge=3,
        le=20,
        description="Video duration in seconds (3-20).",
    )
    resolution: Literal["720p"] = Field(
        default="720p",
        description="Output resolution. Flash is 720p only.",
    )
    aspect_ratio: KlingV4AspectRatio = Field(
        default="16:9",
        description="Aspect ratio of the generated video.",
    )

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class KlingV4FlashImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["kling/v4/flash/image-to-video"]
    prompt: str | None = Field(
        default=None,
        max_length=26000,
        description="Optional text prompt describing the shot.",
    )
    start_image_url: str = Field(
        ...,
        description=(
            "Image to use as the first frame of the video. Flash does not take an end "
            "frame.\n\nMax file size: 30.0MB, Min width: 300px, Min height: 300px, Min "
            "aspect ratio: 0.40, Max aspect ratio: 2.50, Timeout: 20.0s"
        ),
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

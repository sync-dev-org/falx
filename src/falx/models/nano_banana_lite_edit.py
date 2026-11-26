from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.nano_banana_common import NanoBananaExtendedAspectRatio
from falx.models.nano_banana_lite import NanoBananaLiteCommon


class NanoBananaLiteEditConfig(NanoBananaLiteCommon):
    app_id: Literal["google/nano-banana-lite/edit"]
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=50000,
        description="The prompt for image editing.",
    )
    aspect_ratio: NanoBananaExtendedAspectRatio | None = Field(
        default="auto",
        description=(
            "The aspect ratio of the generated image. Supports extreme ratios: 4:1, 1:4, 8:1, 1:8."
        ),
    )
    image_urls: list[str] = Field(
        default_factory=list,
        description=(
            "The URLs of the images to use for image-to-image generation or image editing."
        ),
    )

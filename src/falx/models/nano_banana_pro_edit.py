from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.nano_banana_common import NanoBananaExtendedAspectRatio
from falx.models.nano_banana_pro import NanoBananaProCommon


class NanoBananaProEditConfig(NanoBananaProCommon):
    app_id: Literal["fal-ai/nano-banana-pro/edit", "fal-ai/gemini-3-pro-image-preview/edit"]
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=50000,
        description="The prompt for image editing.",
    )
    image_urls: list[str] = Field(
        default_factory=list,
        description=(
            "The URLs of the images to use for image-to-image generation or image editing."
        ),
    )
    aspect_ratio: NanoBananaExtendedAspectRatio | None = Field(
        default="auto",
        description=("The aspect ratio of the generated image, including 1:4, 4:1, 1:8 and 8:1."),
    )

from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.nano_banana_common import NanoBananaCommon, NanoBananaEditAspectRatio


class NanoBananaEditConfig(NanoBananaCommon):
    app_id: Literal["fal-ai/nano-banana/edit", "fal-ai/gemini-25-flash-image/edit"]
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=50000,
        description="The prompt for image editing.",
    )
    aspect_ratio: NanoBananaEditAspectRatio | None = Field(
        default="auto",
        description="The aspect ratio of the generated image.",
    )
    image_urls: list[str] = Field(
        ...,
        description=(
            "The URLs of the images to use for image-to-image generation or image editing."
        ),
    )

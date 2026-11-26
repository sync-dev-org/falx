from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models.gpt_image_2 import GptImage2Common, ImageSize, ImageSizePreset


class GptImage2EditConfig(GptImage2Common):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["openai/gpt-image-2/edit"]
    image_size: ImageSizePreset | ImageSize = Field(
        default="auto",
        description=(
            "Size of the generated image. Use auto to infer the size from the input "
            "images, or provide a preset name or explicit width and height object."
        ),
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        description="Reference image URLs to use for the generation.",
    )
    mask_url: str | None = Field(
        default=None,
        description="URL of a mask image that indicates which part of the image to edit.",
    )

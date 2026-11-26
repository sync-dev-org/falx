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
        max_length=16,
        description=(
            "The URLs of the images to use as a reference for the generation. A maximum "
            "of 16 images are allowed."
        ),
    )
    mask_url: str | None = Field(
        default=None,
        description="URL of a mask image that indicates which part of the image to edit.",
    )

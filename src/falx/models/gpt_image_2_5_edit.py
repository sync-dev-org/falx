from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.gpt_image_2 import ImageSize, ImageSizePreset
from falx.models.gpt_image_2_5 import GptImage25Common


class GptImage25EditCommon(GptImage25Common):
    """Shared parameters for GPT Image 2.5 edit endpoints."""

    image_size: ImageSizePreset | ImageSize = Field(
        default="auto",
        description="The size of the generated image. Use auto to infer from input images.",
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
        description=(
            "The URL of the mask image to use for the generation. This indicates what "
            "part of the image to edit."
        ),
    )


class GptImage25FlareEditConfig(GptImage25EditCommon):
    app_id: Literal["openai/gpt-image-2.5/flare/edit"]


class GptImage25SunburstEditConfig(GptImage25EditCommon):
    app_id: Literal["openai/gpt-image-2.5/sunburst/edit"]

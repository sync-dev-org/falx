from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from falx.models.gpt_image_2 import ImageSize, ImageSizePreset
from falx.models.gpt_image_2_6 import GptImage26Common


class GptImage26EditCommon(GptImage26Common):
    """Shared parameters for GPT Image 2.6 edit endpoints."""

    image_size: ImageSizePreset | ImageSize = Field(
        default="auto",
        description="The size of the generated image. Use 'auto' to infer from input images.",
    )
    image_urls: list[str] = Field(
        ...,
        max_length=16,
        title="Image URLs",
        description=(
            "The URLs of the images to use as a reference for the generation. A maximum "
            "of 16 images are allowed."
        ),
    )
    mask_url: str | None = Field(
        default=None,
        title="Mask URL",
        description=(
            "Mask image URL. White marks regions to edit and black marks regions to keep."
        ),
    )
    markup_image_url: str | None = Field(
        default=None,
        title="Markup Image URL",
        description=(
            "Transparent PNG containing only annotations (circles, arrows, notes) that "
            "guide the edit of the first image. Must match the first image's dimensions. "
            "Cannot be combined with mask_url. Reference images are sent unmodified when set."
        ),
    )
    output_format: Literal["jpeg", "png", "webp", "gif"] = Field(
        default="png",
        description="Output format for the images. 'gif' returns an animation.",
    )

    @model_validator(mode="after")
    def validate_edit_guidance(self) -> GptImage26EditCommon:
        if self.markup_image_url is not None and self.mask_url is not None:
            raise ValueError("markup_image_url cannot be combined with mask_url")
        return self


class GptImage26FlareEditConfig(GptImage26EditCommon):
    app_id: Literal["openai/gpt-image-2.6/flare/edit"]


class GptImage26SunburstEditConfig(GptImage26EditCommon):
    app_id: Literal["openai/gpt-image-2.6/sunburst/edit"]

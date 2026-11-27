from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.mai_image_2_7 import (
    MaiImage27Common,
    MaiImage27ImageSize,
    MaiImage27ImageSizePreset,
)


class MaiImage27EditCommon(MaiImage27Common):
    """Shared parameters for MAI Image 2.7 and Flash edit endpoints."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="The instruction describing how to edit the input images.",
    )
    image_size: MaiImage27ImageSize | MaiImage27ImageSizePreset | None = Field(
        default=None,
        description=(
            "The size of the edited image. If not set, the model picks a size close to the "
            "input. Each side must be at least 768 pixels and the total pixel count at most "
            "4,194,304 (2048x2048). Custom sizes are rounded down to a multiple of 16."
        ),
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="png",
        description="The format of the edited image.",
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="The URLs of the images to edit or reference (up to 5).",
    )


class MaiImage27EditConfig(MaiImage27EditCommon):
    app_id: Literal["microsoft/mai-image-2.7/edit"]


class MaiImage27FlashEditConfig(MaiImage27EditCommon):
    app_id: Literal["microsoft/mai-image-2.7/flash/edit"]

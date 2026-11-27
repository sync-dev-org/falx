from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.minimax_h3_image_common import (
    MinimaxH3ImageCommon,
    MinimaxH3ImageLoraCommon,
    MinimaxH3ImageSize,
    MinimaxH3ImageSizePreset,
)


class MinimaxH3ImageEditCommon(MinimaxH3ImageCommon):
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=32_000,
        description=(
            "The edit to make. Refer to the input images as Image 1, Image 2, ... "
            "in `image_urls` order."
        ),
    )
    image_size: MinimaxH3ImageSize | MinimaxH3ImageSizePreset | Literal["auto"] = Field(
        default="auto",
        description=(
            "The size of the generated image. Output area must be 655360 to 20000000 "
            "pixels, inclusive, with aspect ratio between 1:3 and 3:1, inclusive. "
            "`auto` keeps the first image's aspect ratio, limited to 1:3..3:1, "
            "within a 2048x2048 area."
        ),
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=16,
        description=(
            "The images to edit or compose, at most 16, in the order the prompt cites "
            "them. Each side must be 128 to 8192 pixels."
        ),
    )


class MinimaxH3ImageEditConfig(MinimaxH3ImageEditCommon, MinimaxH3ImageLoraCommon):
    app_id: Literal["minimax/h3-image/edit"]


class MinimaxH3ImageHighspeedEditConfig(MinimaxH3ImageEditCommon):
    app_id: Literal["minimax/h3-image/highspeed/edit"]

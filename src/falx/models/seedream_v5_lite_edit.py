from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v5_lite_text_to_image import SeedreamV5LiteCommon


class SeedreamV5LiteEditConfig(SeedreamV5LiteCommon):
    app_id: Literal["fal-ai/bytedance/seedream/v5/lite/edit"]
    prompt: str = Field(
        ...,
        description="Text prompt used to edit the input images.",
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description=(
            "Input image URLs for editing. Up to ten input images may be provided. fal's "
            "endpoint uses the last ten images if more are sent; falx validates the "
            "ten-image cap before submission."
        ),
    )

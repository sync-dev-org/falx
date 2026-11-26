from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v5_lite_text_to_image import SeedreamV5LiteCommon


class SeedreamV5LiteEditConfig(SeedreamV5LiteCommon):
    app_id: Literal[
        "fal-ai/bytedance/seedream/v5/lite/edit",
        "bytedance/seedream/v5/lite/edit",
    ]
    prompt: str = Field(
        ...,
        description="Text prompt used to edit the input images.",
    )
    image_urls: list[str] = Field(
        ...,
        description=(
            "List of URLs of input images for editing. When more than 10 references "
            "are provided, only the last 10 are used."
        ),
    )

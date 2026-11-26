from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from falx.models.seedream_v45_text_to_image import SeedreamV45Common


class SeedreamV45EditConfig(SeedreamV45Common):
    app_id: Literal["fal-ai/bytedance/seedream/v4.5/edit"]
    prompt: str = Field(
        ...,
        description="Text prompt used to edit the input images.",
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description=("Input image URLs for editing. Up to ten input images may be provided."),
    )

    @model_validator(mode="after")
    def validate_total_input_and_output_images(self) -> SeedreamV45EditConfig:
        total_images = len(self.image_urls) + self.num_images * self.max_images
        if total_images > 15:
            raise ValueError("total number of images must not exceed 15")
        return self

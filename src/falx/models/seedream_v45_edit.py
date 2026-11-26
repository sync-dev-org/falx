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
        description=(
            "List of URLs of input images for editing. Presently, up to 10 image inputs "
            "are allowed. If over 10 images are sent, only the last 10 will be used."
        ),
    )

    @model_validator(mode="after")
    def validate_total_input_and_output_images(self) -> SeedreamV45EditConfig:
        total_images = len(self.image_urls) + self.num_images * self.max_images
        if total_images > 15:
            raise ValueError("total number of images must not exceed 15")
        return self

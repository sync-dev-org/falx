from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models.kling_v4_image_common import KlingV4ImageCommon, KlingV4ImageElement


class KlingV4ImageToImageConfig(KlingV4ImageCommon):
    app_id: Literal["kling/v4/image-to-image"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description=(
            "Text prompt. Reference images as @Image1, @Image2, ... "
            "and elements as @Element1, @Element2, ..."
        ),
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Reference images (1-10).",
    )
    elements: list[KlingV4ImageElement] | None = Field(
        default=None,
        max_length=7,
        description=(
            "Elements, referenced as @Element1, @Element2, ... (max 7). "
            "Images and elements combined must not exceed 10."
        ),
    )

    @model_validator(mode="after")
    def validate_combined_reference_count(self) -> Self:
        if len(self.image_urls) + len(self.elements or []) > 10:
            raise ValueError("images and elements combined must not exceed 10")
        return self

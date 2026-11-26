from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class VirtualTryOnConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["google/virtual-try-on"]
    person_image_url: str = Field(
        ...,
        description="The URL of the image of the person trying on the product.",
    )
    product_image_url: str = Field(
        ...,
        description="The URL of the product image to try on.",
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=4,
        description="The number of virtual try-on images to generate.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

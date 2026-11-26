from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazProcessImageCommon(BaseFalConfig):
    """Shared inputs for Topaz image adjustment, denoising, restoration, and sharpening."""

    random_seed_field: ClassVar[str | None] = None

    image_url: str = Field(
        ...,
        min_length=1,
        description="Url of the image to process",
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        description="Output format of the processed image.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

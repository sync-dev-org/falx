from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class BriaIncreaseResolutionConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["bria/increase-resolution"]
    image_url: str = Field(
        ...,
        description="URL of the image to upscale.",
    )
    desired_increase: Literal[2, 4] = Field(
        default=2,
        description="Upscale factor. Each factor is its own SwinIR checkpoint.",
    )
    output_type: Literal["png", "jpeg"] = Field(
        default="png",
        description="Image format. JPEG carries no alpha, so preserve_alpha does not apply.",
    )
    preserve_alpha: bool = Field(
        default=True,
        description="Reattach the source alpha channel to the result.",
    )
    preserve_color: bool = Field(
        default=False,
        description="Correct the upscaled result's color cast against the source image.",
    )
    sync_mode: bool = Field(
        default=False,
        description="Return the image inline instead of as a URL.",
    )

from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazUpscaleImageTransparentConfig(BaseFalConfig):
    app_id: Literal["topaz/upscale/image/transparent"]
    image_url: str = Field(
        ...,
        min_length=1,
        description=(
            "Url of the image to process. The fixed 4x upscale supports inputs up to "
            "8000 pixels per side."
        ),
    )
    output_format: Literal["png"] = Field(
        default="png",
        description="Transparent upscaling always outputs PNG to preserve the alpha channel.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

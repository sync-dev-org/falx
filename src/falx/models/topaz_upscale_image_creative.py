from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazUpscaleImageCreativeConfig(BaseFalConfig):
    app_id: Literal["topaz/upscale/image/creative"]
    image_url: str = Field(
        ...,
        min_length=1,
        description="Url of the image to be upscaled",
    )
    model: Literal["Bloom 2", "Bloom", "Bloom Realism"] = Field(
        default="Bloom 2",
        description=(
            "Creative (Bloom) upscaling model. Bloom 2 is the latest and most capable; "
            "Bloom creatively upscales and transforms AI-generated images; Bloom Realism "
            "biases the added detail toward photorealism."
        ),
    )
    upscale_factor: float = Field(
        default=2,
        ge=1,
        le=4,
        description="Factor to upscale the image by (e.g. 2.0 doubles width and height)",
    )
    autoprompt: bool | None = Field(
        default=None,
        description=(
            "Enable automatic prompt generation. Applies to Bloom 2 only; Topaz defaults "
            "it to true when omitted."
        ),
    )
    creativity: int | None = Field(
        default=None,
        ge=1,
        le=9,
        description=(
            "Creativity level (1-9). Higher values produce more creative/hallucinated "
            "details. Applies to Bloom 2 only."
        ),
    )
    color_preservation: bool | None = Field(
        default=None,
        description="Preserve the source image's colors in the output. Applies to Bloom 2 only.",
    )
    crop_to_fill: bool = Field(default=False)
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        description="Output format of the upscaled image.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

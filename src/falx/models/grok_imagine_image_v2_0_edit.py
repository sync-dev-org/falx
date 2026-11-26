from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.grok_imagine_image_v2_0 import (
    GrokImagineImageV20AspectRatio,
    GrokImagineImageV20BaseConfig,
)

GrokImagineImageV20EditAspectRatio = Literal["auto"] | GrokImagineImageV20AspectRatio


class GrokImagineImageV20EditConfig(GrokImagineImageV20BaseConfig):
    app_id: Literal["xai/grok-imagine-image/v2.0/edit"]
    quality: Literal["low", "medium"] = Field(
        default="medium",
        description="Quality level of the edited image.",
    )
    aspect_ratio: GrokImagineImageV20EditAspectRatio = Field(
        default="auto",
        description=(
            "Aspect ratio of the edited image. When set to `auto`, the output preserves "
            "the aspect ratio of the first input image."
        ),
    )
    image_urls: list[str] | None = Field(
        default=None,
        max_length=3,
        description="List of URLs of the images to edit. A maximum of 3 images are supported.",
    )

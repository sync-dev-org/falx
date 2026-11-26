from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.grok_imagine_image_v2_0 import (
    GrokImagineImageV20AspectRatio,
    GrokImagineImageV20BaseConfig,
)

GrokImagineImageV20EditAspectRatio = GrokImagineImageV20AspectRatio


class GrokImagineImageV20EditConfig(GrokImagineImageV20BaseConfig):
    app_id: Literal["xai/grok-imagine-image/v2.0/edit"]
    quality: Literal["low", "medium", "auto"] = Field(
        default="medium",
        description=(
            "Quality level of the edited image. `auto` lets xAI choose; "
            "it currently uses `medium` for editing."
        ),
    )
    aspect_ratio: GrokImagineImageV20EditAspectRatio = Field(
        default="auto",
        description=(
            "Aspect ratio of the edited image. Standard auto uses the nearest "
            "supported ratio of the first reference."
        ),
    )
    image_urls: list[str] | None = Field(
        default=None,
        max_length=5,
        description="List of URLs of the images to edit. A maximum of 5 images are supported.",
    )

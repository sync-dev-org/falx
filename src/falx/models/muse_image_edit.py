from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.muse_image import MuseImageBaseConfig


class MuseImageEditConfig(MuseImageBaseConfig):
    app_id: Literal["meta/muse-image/edit"]
    num_images: int = Field(
        default=1,
        ge=1,
        le=10,
        description="The number of edited images to generate.",
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description=(
            "Reference images used for the edit. Provide between 1 and 10 HTTP(S) "
            "or data URLs."
        ),
    )

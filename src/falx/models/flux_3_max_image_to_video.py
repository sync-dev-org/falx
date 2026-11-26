from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_max_common import Flux3MaxBaseConfig


class Flux3MaxImageToVideoConfig(Flux3MaxBaseConfig):
    app_id: Literal["blackforestlabs/flux-3-max/image-to-video"]
    prompt: str = Field(
        ...,
        min_length=1,
        description="The text prompt describing how the video unfolds from the image.",
    )
    image_url: str = Field(
        ...,
        description="URL of the image the video starts from (PNG, JPEG, or WebP).",
    )
    end_image_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of the image used as the last frame of the video (PNG, JPEG, or WebP)."
        ),
    )

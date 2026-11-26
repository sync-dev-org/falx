from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_common import Flux3BaseConfig, Flux3FlexibleDuration


class Flux3ImageToVideoConfig(Flux3BaseConfig):
    app_id: Literal["blackforestlabs/flux-3/image-to-video"]
    duration: Flux3FlexibleDuration = Field(
        default="auto",
        description=("Duration of the generated video in seconds. `auto` lets the model choose."),
    )
    image_url: str = Field(
        ...,
        description="URL of the image the video starts from (PNG, JPEG, or WebP).",
    )

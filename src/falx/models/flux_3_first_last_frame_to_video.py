from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_common import Flux3BaseConfig, Flux3FixedDuration


class Flux3FirstLastFrameToVideoConfig(Flux3BaseConfig):
    app_id: Literal["blackforestlabs/flux-3/first-last-frame-to-video"]
    duration: Flux3FixedDuration = Field(
        default=5,
        description=(
            "Duration of the generated video in seconds. "
            "An explicit duration is required to place the end frame."
        ),
    )
    start_image_url: str = Field(
        ...,
        description=("URL of the image used as the first frame of the video (PNG, JPEG, or WebP)."),
    )
    end_image_url: str = Field(
        ...,
        description=("URL of the image used as the last frame of the video (PNG, JPEG, or WebP)."),
    )

from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_common import Flux3BaseConfig, Flux3FlexibleDuration


class Flux3ExtendVideoConfig(Flux3BaseConfig):
    app_id: Literal["blackforestlabs/flux-3/extend-video"]
    prompt: str = Field(
        ...,
        description=(
            "The text prompt describing how the video continues from the source clip's "
            "final frames."
        ),
    )
    duration: Flux3FlexibleDuration = Field(
        default="auto",
        description=("Duration of the generated video in seconds. `auto` lets the model choose."),
    )
    video_url: str = Field(
        ...,
        description="URL of the input video. MP4, under 50 MB and under 15 seconds.",
    )

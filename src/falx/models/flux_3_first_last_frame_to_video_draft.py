from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_common import Flux3FixedDuration
from falx.models.flux_3_draft_common import Flux3DraftBaseConfig


class Flux3FirstLastFrameToVideoDraftConfig(Flux3DraftBaseConfig):
    app_id: Literal["blackforestlabs/flux-3/first-last-frame-to-video/draft"]
    duration: Flux3FixedDuration = Field(
        default=5,
        description=(
            "Draft duration in whole seconds from 5 through 20. "
            "An explicit duration pins the two images to the video boundaries."
        ),
    )
    start_image_url: str = Field(
        ...,
        description="URL or data URI of the image used as the first frame of the draft.",
    )
    end_image_url: str = Field(
        ...,
        description="URL or data URI of the image used as the last frame of the draft.",
    )

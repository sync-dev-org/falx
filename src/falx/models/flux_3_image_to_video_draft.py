from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_draft_common import Flux3DraftBaseConfig


class Flux3ImageToVideoDraftConfig(Flux3DraftBaseConfig):
    app_id: Literal["blackforestlabs/flux-3/image-to-video/draft"]
    image_url: str = Field(
        ...,
        description="URL or data URI of the opening keyframe image.",
    )

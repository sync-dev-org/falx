from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_draft_common import Flux3DraftBaseConfig


class Flux3ExtendVideoDraftConfig(Flux3DraftBaseConfig):
    app_id: Literal["blackforestlabs/flux-3/extend-video/draft"]
    video_url: str = Field(
        ...,
        description="URL or data URI of the source MP4, at most 50 MiB.",
    )

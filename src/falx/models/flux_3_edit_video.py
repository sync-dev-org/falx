from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Flux3EditVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["blackforestlabs/flux-3/edit-video"]
    prompt: str = Field(
        ...,
        max_length=4096,
        description=(
            "The text prompt describing how to change the input video. "
            "The clip is re-rendered preserving motion, timing, and framing."
        ),
    )
    video_url: str = Field(
        ...,
        description="URL of the input video. MP4, under 50 MB and under 15 seconds.",
    )
    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=4,
        description=(
            "The safety tolerance level for the generated video. "
            "0 is the strictest and 4 is the most permissive."
        ),
    )

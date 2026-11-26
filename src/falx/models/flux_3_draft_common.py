from __future__ import annotations

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.flux_3_common import Flux3AspectRatio, Flux3FlexibleDuration


class Flux3DraftBaseConfig(BaseFalConfig):
    prompt: str = Field(
        ...,
        description="The text prompt describing the draft video.",
    )
    aspect_ratio: Flux3AspectRatio = Field(
        default="auto",
        description="Aspect ratio of the generated draft. `auto` lets the model choose.",
    )
    duration: Flux3FlexibleDuration = Field(
        default="auto",
        description="Draft duration in whole seconds from 5 through 20, or `auto`.",
    )
    generate_audio: bool = Field(
        default=True,
        description="Whether to generate audio for the draft video.",
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

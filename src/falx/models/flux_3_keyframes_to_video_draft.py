from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models.flux_3_common import (
    Flux3FixedDuration,
    Flux3Keyframe,
    validate_flux_3_keyframe_positions,
)
from falx.models.flux_3_draft_common import Flux3DraftBaseConfig


class Flux3KeyframesToVideoDraftConfig(Flux3DraftBaseConfig):
    app_id: Literal["blackforestlabs/flux-3/keyframes-to-video/draft"]
    duration: Flux3FixedDuration = Field(
        default=5,
        description=(
            "Draft duration in whole seconds from 5 through 20. "
            "An explicit duration is required to validate keyframe positions."
        ),
    )
    keyframes: list[Flux3Keyframe] = Field(
        ...,
        min_length=1,
        max_length=10,
        description=(
            "Keyframe images pinned to frame positions in the generated draft. "
            "Up to 10 keyframes with unique `frame_index` values."
        ),
    )

    @model_validator(mode="after")
    def validate_keyframe_positions(self) -> Self:
        validate_flux_3_keyframe_positions(self.keyframes, self.duration)
        return self

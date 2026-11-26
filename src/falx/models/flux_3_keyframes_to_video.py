from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models.flux_3_common import (
    Flux3BaseConfig,
    Flux3FixedDuration,
    Flux3Keyframe,
    validate_flux_3_keyframe_positions,
)


class Flux3KeyframesToVideoConfig(Flux3BaseConfig):
    app_id: Literal["blackforestlabs/flux-3/keyframes-to-video"]
    duration: Flux3FixedDuration = Field(
        default=5,
        description=(
            "Duration of the generated video in seconds. "
            "An explicit duration is required to validate keyframe positions."
        ),
    )
    keyframes: list[Flux3Keyframe] = Field(
        ...,
        min_length=1,
        max_length=10,
        description=(
            "Keyframe images pinned to frame positions in the generated video. "
            "Up to 10 keyframes with unique `frame_index` values."
        ),
    )

    @model_validator(mode="after")
    def validate_keyframe_positions(self) -> Self:
        validate_flux_3_keyframe_positions(self.keyframes, self.duration)
        return self

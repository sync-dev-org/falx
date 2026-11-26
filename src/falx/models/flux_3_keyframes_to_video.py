from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models.flux_3_common import (
    Flux3BaseConfig,
    Flux3FixedDuration,
    Flux3Keyframe,
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
        frame_indexes = [keyframe.frame_index for keyframe in self.keyframes]
        if len(set(frame_indexes)) != len(frame_indexes):
            raise ValueError("keyframe frame_index values must be unique")

        maximum_frame_index = self.duration * 24
        if any(frame_index > maximum_frame_index for frame_index in frame_indexes):
            raise ValueError("keyframe frame_index must be at most duration * 24")
        return self

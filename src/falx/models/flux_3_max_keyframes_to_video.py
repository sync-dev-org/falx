from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models.flux_3_common import Flux3Keyframe
from falx.models.flux_3_max_common import Flux3MaxBaseConfig


class Flux3MaxKeyframesToVideoConfig(Flux3MaxBaseConfig):
    app_id: Literal["blackforestlabs/flux-3-max/keyframes-to-video"]
    prompt: str = Field(
        ...,
        min_length=1,
        description="The text prompt describing how the video moves between keyframes.",
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
        if any(frame_index > self.duration * 24 for frame_index in frame_indexes):
            raise ValueError("keyframe frame_index must be at most duration * 24")
        return self

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from falx.models import BaseFalConfig

Flux3Resolution = Literal["720p", "1080p"]
Flux3AspectRatio = Literal["auto", "21:9", "2:1", "16:9", "4:3", "1:1", "3:4", "9:16"]
Flux3FlexibleDuration = Literal["auto", 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
Flux3FixedDuration = Literal[5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]


class Flux3BaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    prompt: str = Field(
        ...,
        description="The text prompt describing the video you want to generate.",
    )
    resolution: Flux3Resolution = Field(
        default="720p",
        description="Resolution of the generated video.",
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
    generate_audio: bool = Field(
        default=True,
        description="Whether to generate audio for the video.",
    )
    aspect_ratio: Flux3AspectRatio = Field(
        default="auto",
        description="Aspect ratio of the generated video. `auto` lets the model choose.",
    )


class Flux3Keyframe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_url: str = Field(
        ...,
        description="URL of the keyframe image (PNG, JPEG, or WebP).",
    )
    frame_index: int = Field(
        ...,
        ge=0,
        description=(
            "Frame position of this keyframe in the generated 24 fps video. "
            "Must be unique and at most `duration * 24`."
        ),
    )

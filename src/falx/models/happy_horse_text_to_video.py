from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class HappyHorseTextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["alibaba/happy-horse/text-to-video"]
    prompt: str = Field(
        ...,
        max_length=2500,
        description="Text prompt describing the desired video.",
    )
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4"] = Field(
        default="16:9",
        description="Aspect ratio of the generated video.",
    )
    resolution: Literal["720p", "1080p"] = Field(
        default="1080p",
        description="Output video resolution tier.",
    )
    duration: Literal[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] = Field(
        default=5,
        description=(
            "Output video duration in seconds. "
            "Allowed values: 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 (int)."
        ),
    )
    seed: int | None = Field(
        default=None,
        ge=0,
        le=2_147_483_647,
        description="Random seed for reproducibility.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Enable content moderation for input and output.",
    )

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MinimaxH3MaxRelightConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max/relight"]
    video_url: str = Field(
        ...,
        min_length=1,
        description=(
            "Source video up to 15 seconds long. Converted to constant 24 fps and "
            "trimmed at the end to the closest 17n+5 frame count, with at least "
            "56 frames (about 2.33 seconds) remaining. The output matches this "
            "prepared video's frame count and duration."
        ),
    )
    reference_image_url: str = Field(
        ...,
        min_length=1,
        description="Sphere render showing the target lighting.",
    )
    resolution: Literal["480P", "768P", "1080P", "2K"] = Field(
        default="768P",
        description=(
            "Output video resolution. 480P and 768P generate natively; 1080P and "
            "2K (1440p) use latent upscaling and refinement from 768P."
        ),
    )
    aspect_ratio: Literal["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="16:9",
        description="Output video aspect ratio.",
    )
    seed: int | None = Field(
        default=None,
        description="Random seed for video generation.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Enable safety checking.",
    )
    sync_mode: bool = Field(
        default=False,
        description="Return video as a data URI.",
    )

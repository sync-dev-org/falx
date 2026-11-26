from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MinimaxH3MaxReframeVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max/reframe-video"]
    prompt: str = Field(
        default="",
        max_length=50_000,
        description=(
            "Optional guidance for the new surroundings. Expansion captions "
            "the source automatically."
        ),
    )
    video_url: str = Field(
        ...,
        description=(
            "Source video, 0.25 to 300 seconds; fitted onto the target canvas "
            "with its timeline and audio preserved."
        ),
    )
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "9:21"] = Field(
        default="16:9",
        description=(
            "Target canvas aspect ratio; the source is contain-fitted and the rest is outpainted."
        ),
    )
    resolution: Literal["480p", "768p", "1080p"] = Field(
        default="768p",
        description=(
            "Target canvas resolution profile. 1080p uses learned latent "
            "upscaling from a native 768p reframe."
        ),
    )
    seed: int | None = Field(default=None, ge=0, le=4_294_967_295)
    enable_safety_checker: bool = Field(default=True)

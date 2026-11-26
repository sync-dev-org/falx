from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MinimaxH3MaxRecastConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max/recast"]
    video_url: str = Field(
        ...,
        description=(
            "The source video, 5 to 30 seconds long, with no single shot longer than 15 seconds."
        ),
    )
    reference_image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=4,
        description=(
            "One photo per new person. By default they replace the main people "
            "in the video from left to right, each in every shot they appear in."
        ),
    )
    prompt: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional: who becomes whom, or what else to keep or change.",
    )
    resolution: Literal["768P", "1080P"] = Field(default="1080P")
    seed: int | None = Field(
        default=None,
        ge=0,
        description="Random seed. Leave empty for a random one.",
    )
    enhance_realism: bool = Field(
        default=False,
        description=(
            "More natural skin textures and better blending of the new people "
            "into the scene. Off unless set."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

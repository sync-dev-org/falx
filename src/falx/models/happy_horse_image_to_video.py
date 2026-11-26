from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class HappyHorseImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["alibaba/happy-horse/image-to-video"]
    image_url: str = Field(
        ...,
        description=(
            "URL of the first frame image. Supported formats are JPEG, JPG, PNG, BMP, and WEBP."
        ),
    )
    prompt: str | None = Field(
        default=None,
        max_length=2500,
        description="Optional text prompt guiding the animation.",
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

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.flux_3_common import Flux3AspectRatio, Flux3FixedDuration


class Flux3MaxBaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        min_length=1,
        description="The text prompt describing the video you want to generate.",
    )
    duration: Flux3FixedDuration = Field(
        default=5,
        description="Duration of the generated video in seconds.",
    )
    resolution: Literal["720p", "1080p", "2K", "4K"] = Field(
        default="720p",
        description=(
            "Resolution of the generated video. `1080p`, `2K` (1440p) and `4K` (2160p) "
            "are upscaled from the 720p generation; exact dimensions depend on the aspect ratio."
        ),
    )
    reasoning_level: Literal["low", "high"] = Field(
        default="high",
        description=(
            "How much effort the harness spends reasoning about the given prompt. "
            "Higher reasoning effort means slower generation time."
        ),
    )
    aspect_ratio: Flux3AspectRatio = Field(
        default="auto",
        description=(
            "Aspect ratio of the generated video. `auto` uses 16:9 for text prompts "
            "and follows the first image otherwise."
        ),
    )
    generate_audio: bool = Field(
        default=True,
        description="Whether to generate audio for the video.",
    )
    seed: int | None = Field(
        default=None,
        description="The seed to use for the generation. Random when not provided.",
    )

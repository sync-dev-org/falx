from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class ViduQ4BaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    duration: int = Field(
        default=5,
        ge=3,
        le=16,
        description="Duration of the video in seconds (3-16)",
    )
    seed: int | None = Field(
        default=None,
        description="Random seed for reproducibility. If None, a random seed is chosen.",
    )
    resolution: Literal["540p", "720p", "1080p", "2K", "4K"] = Field(
        default="720p",
        description="Output video resolution",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

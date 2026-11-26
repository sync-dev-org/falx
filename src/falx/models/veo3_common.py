from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Veo3Common(BaseFalConfig):
    """Shared parameters for Veo 3 regular and fast video generation."""

    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        max_length=20_000,
        description="The text prompt describing the video you want to generate",
    )
    aspect_ratio: Literal["16:9", "9:16"] = Field(
        default="16:9",
        description="The aspect ratio of the generated video.",
    )
    duration: Literal["4s", "6s", "8s"] = Field(
        default="8s",
        description="The duration of the generated video.",
    )
    negative_prompt: str | None = Field(
        default=None,
        description="A negative prompt to guide the video generation.",
    )
    resolution: Literal["720p", "1080p"] = Field(
        default="720p",
        description="The resolution of the generated video.",
    )
    generate_audio: bool = Field(
        default=True,
        description="Whether to generate audio for the video.",
    )
    seed: int | None = Field(
        default=None,
        description="The seed for the random number generator.",
    )
    auto_fix: bool = Field(
        default=True,
        description=(
            "Whether to automatically attempt to fix prompts that fail content policy "
            "or other validation checks by rewriting them."
        ),
    )
    safety_tolerance: Literal["1", "2", "3", "4", "5", "6"] = Field(
        default="4",
        description=(
            "The safety tolerance level for content moderation. 1 is the most strict "
            "(blocks most content), 6 is the least strict."
        ),
    )

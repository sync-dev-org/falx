from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class NanoBanana2Common(BaseFalConfig):
    """Shared parameters for nano-banana-2 text and edit endpoints."""

    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        min_length=3,
        max_length=50000,
        description="Text prompt that describes the image to generate.",
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of images to generate for the request.",
    )
    limit_generations: bool = Field(
        default=True,
        description=(
            "Limits each round of prompting to one generated image, ignoring prompt "
            "instructions that ask for more images or intermediate images. This is "
            "experimental and may affect generation quality."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "When true, generated media is returned as a data URI and is not available "
            "in request history."
        ),
    )
    system_prompt: str = Field(
        default="",
        description=(
            "Optional system instruction that steers the model persona and output "
            "style across the request. Leave blank to omit."
        ),
    )
    resolution: Literal["0.5K", "1K", "2K", "4K"] = Field(
        default="1K",
        description="Resolution of the generated image.",
    )
    aspect_ratio: (
        Literal[
            "auto",
            "21:9",
            "16:9",
            "3:2",
            "4:3",
            "5:4",
            "1:1",
            "4:5",
            "3:4",
            "2:3",
            "9:16",
            "4:1",
            "1:4",
            "8:1",
            "1:8",
        ]
        | None
    ) = Field(
        default="auto",
        description=(
            "Aspect ratio of the generated image. Use auto to let the model decide from the prompt."
        ),
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="png",
        description="File format for generated images.",
    )
    thinking_level: Literal["minimal", "high"] | None = Field(
        default=None,
        description=(
            "Optional model thinking level. Set minimal or high to include model "
            "thoughts in generation; omit to disable thinking."
        ),
    )
    safety_tolerance: Literal["1", "2", "3", "4", "5", "6"] = Field(
        default="4",
        description=(
            "Content moderation tolerance for API calls, where 1 is most strict and "
            "6 is least strict."
        ),
    )
    enable_web_search: bool = Field(
        default=False,
        description="Allows the image generation task to use current web information.",
    )
    seed: int | None = Field(
        default=None,
        description="Seed for the random number generator.",
    )


class NanoBanana2Config(NanoBanana2Common):
    app_id: Literal["fal-ai/nano-banana-2"]

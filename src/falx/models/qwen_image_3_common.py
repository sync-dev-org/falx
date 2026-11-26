from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

QwenImage3ImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
]
QwenImage3OutputFormat = Literal["jpeg", "png", "webp"]


class QwenImage3ImageSize(BaseFalConfig):
    width: int = Field(
        default=512,
        gt=0,
        le=14142,
        description="The width of the generated image.",
    )
    height: int = Field(
        default=512,
        gt=0,
        le=14142,
        description="The height of the generated image.",
    )


class QwenImage3Common(BaseFalConfig):
    """Shared parameters for Qwen Image 3 text and edit endpoints."""

    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description=(
            "Text prompt describing the desired image. Supports Chinese and English. "
            "Max 5000 characters."
        ),
    )
    negative_prompt: str | None = Field(
        default="",
        max_length=500,
        description="Content to avoid in the generated image. Max 500 characters.",
    )
    image_size: QwenImage3ImageSizePreset | QwenImage3ImageSize = Field(
        default="square_hd",
        description=(
            "The size of the generated image. Total number of pixels must be between "
            "512x512 and 2048x2048."
        ),
    )
    enable_prompt_expansion: bool = Field(
        default=True,
        description="Enable automatic LLM prompt rewriting for better results.",
    )
    seed: int | None = Field(
        default=None,
        ge=0,
        le=2_147_483_647,
        description="Random seed for reproducibility (0-2147483647).",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Enable content moderation for input and output. Disabling it requires "
            "account authorization; unauthorized requests are always checked."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If true, the media is returned as a data URI and the output data is not "
            "available in the request history."
        ),
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=6,
        description="The number of images to generate.",
    )
    output_format: QwenImage3OutputFormat = Field(
        default="png",
        description="The format of the generated image.",
    )

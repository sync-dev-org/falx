from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

ImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
    "auto",
]


class ImageSize(BaseFalConfig):
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


class GptImage2Common(BaseFalConfig):
    """Shared parameters for GPT-Image-2 text and edit endpoints."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=32000,
        description="Prompt for image generation.",
    )
    image_size: ImageSizePreset | ImageSize = Field(
        default="landscape_4_3",
        description=(
            "The size of the generated image. Supports preset names, explicit {width, height}, "
            "or 'auto' to let the model pick the best size. Concrete sizes must have both "
            "dimensions as multiples of 16, max edge 3840px, aspect ratio <= 3:1, total pixels "
            "between 655,360 and 8,294,400."
        ),
    )
    quality: Literal["auto", "low", "medium", "high"] = Field(
        default="high",
        description=(
            "Quality setting for generated images. Use auto to let the model choose "
            "the best quality for the prompt."
        ),
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of images to generate.",
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="png",
        description="Output file format for generated images.",
    )
    background: Literal["auto", "transparent", "opaque"] = Field(
        default="auto",
        description="Background for the generated image",
    )
    output_compression: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description=(
            "Compression level from 0 to 100. Only supported when output_format is "
            "'jpeg' or 'webp'."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "When true, generated media is returned as a data URI and is not available "
            "in request history."
        ),
    )


class GptImage2Config(GptImage2Common):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["openai/gpt-image-2"]

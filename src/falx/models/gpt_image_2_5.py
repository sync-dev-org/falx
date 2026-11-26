from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.gpt_image_2 import ImageSize, ImageSizePreset


class GptImage25Common(BaseFalConfig):
    """Shared parameters for GPT Image 2.5 text-to-image and edit endpoints."""

    random_seed_field: ClassVar[str | None] = None

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=32_000,
        description="The prompt for image generation.",
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
    quality: Literal["auto", "low", "medium", "high", "xhigh", "max"] = Field(
        default="high",
        description=(
            "Quality for the generated image. Higher settings increase detail, "
            "latency, and token usage. Use auto to let the model choose."
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
        description="Output format for the images.",
    )
    background: Literal["auto", "transparent", "opaque"] = Field(
        default="auto",
        description="Background for the generated image.",
    )
    output_compression: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description=(
            "Compression level from 0 to 100. Only supported when output_format is jpeg or webp."
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


class GptImage25FlareTextToImageConfig(GptImage25Common):
    app_id: Literal["openai/gpt-image-2.5/flare/text-to-image"]


class GptImage25SunburstTextToImageConfig(GptImage25Common):
    app_id: Literal["openai/gpt-image-2.5/sunburst/text-to-image"]

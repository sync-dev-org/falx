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
        ...,
        description=(
            "Custom image width in pixels. Concrete sizes must use dimensions that "
            "are multiples of 16."
        ),
    )
    height: int = Field(
        ...,
        description=(
            "Custom image height in pixels. Concrete sizes must use dimensions that "
            "are multiples of 16."
        ),
    )


class GptImage2Common(BaseFalConfig):
    """Shared parameters for GPT-Image-2 text and edit endpoints."""

    prompt: str = Field(
        ...,
        min_length=2,
        max_length=32000,
        description="Prompt for image generation.",
    )
    image_size: ImageSizePreset | ImageSize = Field(
        default="landscape_4_3",
        description=(
            "Size of the generated image. Use a preset name, an explicit width and "
            "height object, or auto to let the model pick the best size."
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
        le=4,
        description="Number of images to generate.",
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="png",
        description="Output file format for generated images.",
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

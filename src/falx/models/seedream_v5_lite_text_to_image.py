from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig

SeedreamV5LiteImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
    "auto_2K",
    "auto_3K",
    "auto_4K",
]


class SeedreamV5LiteImageSize(BaseFalConfig):
    width: int = Field(
        default=512,
        gt=0,
        description="Custom generated image width in pixels.",
    )
    height: int = Field(
        default=512,
        gt=0,
        description="Custom generated image height in pixels.",
    )


class SeedreamV5LiteCommon(BaseFalConfig):
    """Shared parameters for Seedream 5.0 Lite text and edit endpoints."""

    prompt: str = Field(
        ...,
        description="Text prompt used to generate or edit the image.",
    )
    image_size: SeedreamV5LiteImageSizePreset | SeedreamV5LiteImageSize = Field(
        default="auto_2K",
        description=(
            "Size of the generated image. Use a preset name or explicit width and height "
            "object. Allowed presets: square_hd, square, portrait_4_3, portrait_16_9, "
            "landscape_4_3, landscape_16_9, auto_2K, auto_3K, auto_4K. fal scales custom "
            "sizes into its supported total-pixel range when needed."
        ),
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=6,
        description="Number of separate model generations to run with the prompt.",
    )
    max_images: int = Field(
        default=1,
        ge=1,
        le=6,
        description=(
            "Maximum images the model may return for each generation. The final image count "
            "can range from num_images through max_images multiplied by num_images."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "When true, generated media is returned as a data URI and is not available "
            "in request history."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Enables the safety checker for the request.",
    )


class SeedreamV5LiteTextToImageConfig(SeedreamV5LiteCommon):
    app_id: Literal["fal-ai/bytedance/seedream/v5/lite/text-to-image"]
    prompt: str = Field(
        ...,
        description="Text prompt used to generate the image.",
    )
    return_byteplus_urls: bool = Field(
        default=False,
        description=(
            "When true, return BytePlus trusted URLs for generated images. fal notes these "
            "URLs expire in 24 hours."
        ),
    )

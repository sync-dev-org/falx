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
        le=16384,
        description="Custom generated image width in pixels.",
    )
    height: int = Field(
        default=512,
        gt=0,
        le=16384,
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
            "The size of the generated image. Custom dimensions within the provider's "
            "pixel and aspect limits are sent unchanged. Other sizes use compatible "
            "scaling. The provider's native pixel range is 2560x1440 to 4096x4096, "
            "with aspect ratio between 1/16 and 16."
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
        le=15,
        description=(
            "Maximum images per generation in sequential mode. Ignored when sequential "
            "generation is disabled. Combined input references and outputs per generation "
            "cannot exceed 15."
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
        description=(
            "Enables the safety checker. Disabling it requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        description="The file format of the generated images.",
    )
    watermark: bool = Field(
        default=False,
        description="Whether to add the provider's visible watermark.",
    )
    sequential_image_generation: Literal["auto", "disabled"] | None = Field(
        default=None,
        description=(
            "Generate related images with auto, or one image per generation with disabled. "
            "When omitted, values of max_images above one enable auto."
        ),
    )


class SeedreamV5LiteTextToImageConfig(SeedreamV5LiteCommon):
    app_id: Literal[
        "fal-ai/bytedance/seedream/v5/lite/text-to-image",
        "bytedance/seedream/v5/lite/text-to-image",
    ]
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

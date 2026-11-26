from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v5_pro_common import SeedreamV5ProCommon, SeedreamV5ProImageSize

SeedreamV5FlashImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
    "auto_1K",
    "auto_1.5K",
    "auto_2K",
]


class SeedreamV5FlashCommon(SeedreamV5ProCommon):
    """Shared generation parameters for Seedream 5 Flash and Pro US."""

    image_size: SeedreamV5ProImageSize | SeedreamV5FlashImageSizePreset = Field(
        default="auto_2K",
        description=(
            "The size of the generated image. Total pixels must be between "
            "921600 and 4624220, with aspect ratio between 1/16 and 16."
        ),
    )
    watermark: bool = Field(
        default=False,
        description="Whether to add the provider's visible watermark.",
    )

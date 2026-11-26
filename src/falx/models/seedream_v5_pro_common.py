from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig

SeedreamV5ProImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
    "auto_1K",
    "auto_2K",
]


class SeedreamV5ProImageSize(BaseFalConfig):
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


class SeedreamV5ProCommon(BaseFalConfig):
    """Shared parameters for Seedream 5.0 Pro text and edit endpoints."""

    prompt: str = Field(
        ...,
        description="Text prompt used to generate or edit the image.",
    )
    image_size: SeedreamV5ProImageSize | SeedreamV5ProImageSizePreset = Field(
        default="auto_2K",
        description=(
            "The size of the generated image. Total pixels must be between "
            "1024x1024 and 2048x2048, with aspect ratio between 1/16 and 16."
        ),
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=6,
        description="Number of separate model generations to run with the prompt.",
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        description="The file format of the generated image.",
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

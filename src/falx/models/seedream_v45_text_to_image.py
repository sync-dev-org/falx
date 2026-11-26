from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

SeedreamV45ImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
    "auto_2K",
    "auto_4K",
]


class SeedreamV45ImageSize(BaseFalConfig):
    width: int = Field(
        default=512,
        gt=0,
        le=14142,
        description="Custom generated image width in pixels.",
    )
    height: int = Field(
        default=512,
        gt=0,
        le=14142,
        description="Custom generated image height in pixels.",
    )


class SeedreamV45Common(BaseFalConfig):
    """Shared parameters for Seedream 4.5 text and edit endpoints."""

    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        description="Text prompt used to generate or edit the image.",
    )
    image_size: SeedreamV45ImageSizePreset | SeedreamV45ImageSize = Field(
        default_factory=lambda: {"width": 2048, "height": 2048},
        validate_default=True,
        description=(
            "Size of the generated image. Use a preset name or explicit width and height object."
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
        description="Maximum images the model may return for each generation.",
    )
    seed: int | None = Field(
        default=None,
        description="Random seed to control image generation stochasticity.",
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


class SeedreamV45TextToImageConfig(SeedreamV45Common):
    app_id: Literal["fal-ai/bytedance/seedream/v4.5/text-to-image"]

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

MarigoldV2ImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
]


class MarigoldV2ImageSize(BaseFalConfig):
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


class MarigoldV2Config(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["fal-ai/marigold-v2"]
    prediction_type: Literal["depth", "see-through-depth", "normals", "albedo"] = Field(
        default="depth",
        description="Prediction map to generate.",
    )
    image_url: str = Field(
        ...,
        description="Input image url.",
    )
    image_size: MarigoldV2ImageSizePreset | MarigoldV2ImageSize | None = Field(
        default=None,
        description=(
            "Inference size as an explicit `{width, height}` object or a preset string "
            '(e.g. `"square_hd"`, `"landscape_4_3"`). Both dimensions must be multiples of '
            "16 and no larger than 2048 pixels on either side, with an aspect ratio between "
            "1:16 and 16:1. Defaults to the input image's dimensions rounded to the nearest "
            "multiple of 16."
        ),
    )
    seed: int | None = Field(
        default=None,
        description=(
            "Random seed. Only affects the VAE encoder's latent sampling (the forward pass "
            "itself is a single deterministic step); the same seed and image reproduce "
            "the same output."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

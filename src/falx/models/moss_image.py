from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

MossImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
]


class MossImageSize(BaseFalConfig):
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


class MossImageConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["fal-ai/moss-image"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=16384,
        description=(
            "Text prompt for image generation. Supports natural language, tag sequences, "
            "and JSON layouts."
        ),
    )
    negative_prompt: str = Field(
        default="",
        max_length=16384,
        description=(
            "Negative prompt. When empty, guidance uses transformer layer skipping "
            "for the negative branch."
        ),
    )
    enable_prompt_expansion: bool = Field(
        default=True,
        description=(
            "Plan a structured layout from your prompt before generation. Preserves "
            "requested visible text and uses the selected image dimensions. If "
            "enhancement is unavailable, uses the original prompt."
        ),
    )
    image_size: MossImageSizePreset | MossImageSize = Field(
        default="square_hd",
        description=(
            "Output image size. Width and height are rounded to multiples of 16 "
            "between 512 and 2048 pixels."
        ),
    )
    num_inference_steps: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Number of denoising steps.",
    )
    guidance_scale: float = Field(
        default=3,
        ge=0,
        le=10,
        description="Classifier-free guidance scale.",
    )
    seed: int | None = Field(
        default=None,
        description="Random seed for reproducible generation.",
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of images to generate.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Enable output content moderation. Disabling it requires account "
            "authorization; unauthorized requests are always checked, and images "
            "flagged as unsafe are returned as black images."
        ),
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="jpeg",
        description="Output image format.",
    )
    sync_mode: bool = Field(
        default=False,
        description="Return images as data URIs instead of storing them in request history.",
    )

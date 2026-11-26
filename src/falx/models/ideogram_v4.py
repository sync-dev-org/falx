from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

IdeogramV4ImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
]


class IdeogramV4ImageSize(BaseFalConfig):
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


class IdeogramV4Config(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["ideogram/v4"]
    prompt: str = Field(
        ...,
        description="The prompt to generate an image from.",
    )
    expansion_model: Literal["None", "Medium", "Large"] = Field(
        default="Medium",
        description=(
            "Which model expands the prompt. 'None' disables prompt expansion and skips "
            "its fee; 'Medium' is fast; 'Large' uses Ideogram's Magic Prompt for the "
            "highest quality."
        ),
    )
    image_size: IdeogramV4ImageSizePreset | IdeogramV4ImageSize = Field(
        default="square_hd",
        description="The resolution of the generated image.",
    )
    rendering_speed: Literal["TURBO", "BALANCED", "QUALITY"] = Field(
        default="BALANCED",
        description="The rendering speed to use. Faster speeds use fewer denoising steps.",
    )
    acceleration: Literal["none", "low", "regular", "high"] = Field(
        default="none",
        description="The acceleration level to use for the image generation.",
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of images to generate.",
    )
    seed: int | None = Field(
        default=None,
        description="The seed to use for generation. A random seed is used when omitted.",
    )
    sync_mode: bool = Field(
        default=False,
        description="When true, the image is returned as a data URI and is not stored.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Enable the safety checker. Disabling it requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        description="The format of the generated image.",
    )

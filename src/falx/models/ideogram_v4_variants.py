from __future__ import annotations

from typing import Annotated, ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.ideogram_v4 import (
    IdeogramV4Config,
    IdeogramV4ImageSize,
    IdeogramV4ImageSizePreset,
)


class IdeogramV4InstantConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["ideogram/v4/instant"]
    prompt: str = Field(
        ...,
        description="The prompt to generate an image from.",
    )
    expansion_model: Literal["None", "Medium"] = Field(
        default="Medium",
        description=(
            "Which model expands the prompt. 'None' disables expansion; "
            "'Medium' uses the fast magic prompt model."
        ),
    )
    image_size: IdeogramV4ImageSizePreset | IdeogramV4ImageSize = Field(
        default="square_hd",
        description="The resolution of the generated image.",
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of images to generate.",
    )
    seed: int | None = Field(
        default=None,
        description=(
            "The seed to use for generation. If not provided, a random seed will be used."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description="If `True`, the image is returned as a data URI and is not stored.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "If set to true, the safety checker will be enabled. Disabling it requires "
            "account authorization; unauthorized requests are always checked."
        ),
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        description="The format of the generated image.",
    )


class IdeogramV4FastConfig(IdeogramV4InstantConfig):
    app_id: Literal["ideogram/v4/fast"]
    rendering_speed: Literal["TURBO", "BALANCED", "QUALITY"] = Field(
        default="BALANCED",
        description="The rendering speed to use. Faster speeds use fewer denoising steps.",
    )


class _IdeogramV4StandardConfig(IdeogramV4Config):
    seed: int | None = Field(
        default=None,
        description=(
            "The seed to use for generation. If not provided, a random seed will be used."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description="If `True`, the image is returned as a data URI and is not stored.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "If set to true, the safety checker will be enabled. Disabling it requires "
            "account authorization; unauthorized requests are always checked."
        ),
    )


class IdeogramV4LoRAInput(BaseFalConfig):
    path: str = Field(
        ...,
        description="URL to an Ideogram V4 LoRA weights file (.safetensors).",
    )
    scale: float = Field(
        default=1.0,
        ge=0,
        le=4,
        description="Scale factor for the LoRA weights.",
    )


IdeogramV4LoRAWeights = Annotated[
    list[IdeogramV4LoRAInput],
    Field(max_length=3, description="List of LoRA weights to apply (maximum 3)."),
]


class IdeogramV4LoraConfig(_IdeogramV4StandardConfig):
    app_id: Literal["ideogram/v4/lora"]
    loras: IdeogramV4LoRAWeights = Field(default_factory=list)


class IdeogramV4ImageToImageConfig(_IdeogramV4StandardConfig):
    app_id: Literal["ideogram/v4/image-to-image"]
    image_size: IdeogramV4ImageSizePreset | Literal["auto"] | IdeogramV4ImageSize = Field(
        default="auto",
        description=(
            "The output image size. Use 'auto' to match the input image size "
            "(capped at ~25MP, up to 8192px per side)."
        ),
    )
    image_url: str = Field(
        ...,
        description="URL of the input image for image-to-image generation.",
    )
    strength: float = Field(
        default=0.8,
        ge=0,
        le=1,
        description=(
            "How much to transform the input image. 1.0 ignores the input image entirely; "
            "lower values stay closer to it."
        ),
    )


class IdeogramV4ImageToImageLoraConfig(IdeogramV4ImageToImageConfig):
    app_id: Literal["ideogram/v4/image-to-image/lora"]
    loras: IdeogramV4LoRAWeights = Field(default_factory=list)


class IdeogramV4TilingConfig(_IdeogramV4StandardConfig):
    app_id: Literal["ideogram/v4/tiling"]
    image_size: IdeogramV4ImageSizePreset | IdeogramV4ImageSize = Field(
        default="square_hd",
        description="The resolution of the generated seamlessly tileable image.",
    )
    image_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of an image. When provided without `mask_url`, performs "
            "image-to-image tiling; with `mask_url`, performs inpainting tiling."
        ),
    )
    mask_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of a mask image for inpainting tiling. White regions are "
            "regenerated, black regions are preserved. Requires `image_url`."
        ),
    )
    strength: float = Field(
        default=0.8,
        ge=0,
        le=1,
        description=(
            "How much to transform the input image. Only used when `image_url` is provided."
        ),
    )
    tiling_mode: Literal["both", "horizontal", "vertical"] = Field(
        default="both",
        description=(
            "Tiling direction: 'both' (omnidirectional), 'horizontal' (left-right only), "
            "or 'vertical' (top-bottom only)."
        ),
    )


class IdeogramV4TilingLoraConfig(IdeogramV4TilingConfig):
    app_id: Literal["ideogram/v4/tiling/lora"]
    loras: IdeogramV4LoRAWeights = Field(default_factory=list)

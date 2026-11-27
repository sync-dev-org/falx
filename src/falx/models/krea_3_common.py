from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

Krea3ImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
    "auto",
]
KREA3_IMAGE_SIZE_LIMITS = {
    "min_width": 256,
    "multiple_of": 16,
    "max_height": 3200,
    "max_area": 4220160,
    "max_width": 3200,
    "min_height": 256,
}


class Krea3ImageSize(BaseFalConfig):
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


class Krea3LoRAInput(BaseFalConfig):
    path: str = Field(
        ...,
        description="HTTPS URL of the LoRA weights. Only .safetensors files are accepted.",
    )
    scale: float = Field(
        default=1.0,
        ge=0,
        le=4,
        description="Scale factor for LoRA application (0.0 to 4.0).",
    )


class Krea3LoraConfig(BaseFalConfig):
    loras: list[Krea3LoRAInput] = Field(
        default_factory=list,
        max_length=3,
        description=(
            "LoRA weights to apply (maximum 3), in the Krea 3 trainer, PEFT or kohya format. "
            "A file without alpha tensors is applied with alpha equal to its rank, "
            "as diffusers does."
        ),
    )


class Krea3Common(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    negative_prompt: str = Field(
        default="",
        max_length=1024,
        description="What to keep out of the image.",
    )
    output_format: Literal["png", "jpeg"] = Field(
        default="png",
        description="Output image format.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Check output images for unsafe content. Disabling requires account authorization."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description="Return images as data URIs instead of saving them in request history.",
    )
    seed: int | None = Field(
        default=None,
        description="Latent noise seed. Use a new seed when editing a previous output again.",
    )
    image_size: Krea3ImageSize | Krea3ImageSizePreset = Field(
        default="auto",
        description=(
            "Output size, rounded up to multiples of 16, at most 4,220,160 total pixels "
            "(1680×2512). auto lets the prompt expander pick the aspect ratio at about 2048×2048."
        ),
        json_schema_extra={"x-fal": KREA3_IMAGE_SIZE_LIMITS},
    )

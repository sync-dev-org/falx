from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig

RecraftV41FlashV2ImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
]


class RecraftV41FlashV2ImageSize(BaseFalConfig):
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


class RecraftV41FlashV2RGBColor(BaseFalConfig):
    r: int = Field(default=0, ge=0, le=255, description="Red color value")
    g: int = Field(default=0, ge=0, le=255, description="Green color value")
    b: int = Field(default=0, ge=0, le=255, description="Blue color value")


class RecraftV41FlashV2TextToImageConfig(BaseFalConfig):
    app_id: Literal["recraft/v4.1/flash/v2/text-to-image"]
    prompt: str = Field(..., min_length=1, max_length=10000)
    image_size: RecraftV41FlashV2ImageSizePreset | RecraftV41FlashV2ImageSize = Field(
        default="square_hd",
    )
    colors: list[RecraftV41FlashV2RGBColor] = Field(
        default_factory=list,
        description="An array of preferable colors",
    )
    background_color: RecraftV41FlashV2RGBColor | None = Field(
        default=None,
        description="The preferable background color of the generated images.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "If set to true, the safety checker will be enabled. Disabling it requires "
            "account authorization; unauthorized requests are always checked."
        ),
    )

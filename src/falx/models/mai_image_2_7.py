from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig

MaiImage27ImageSizePreset = Literal[
    "square_hd",
    "portrait_4_3",
    "landscape_4_3",
    "portrait_3_2",
    "landscape_3_2",
    "portrait_16_9",
    "landscape_16_9",
]


class MaiImage27ImageSize(BaseFalConfig):
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


class MaiImage27Common(BaseFalConfig):
    """Shared parameters for MAI Image 2.7 and Flash endpoints."""

    random_seed_field: ClassVar[str | None] = None

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="The text prompt to generate an image from.",
    )
    background: Literal["opaque", "transparent"] = Field(
        default="opaque",
        description='Use "transparent" for a transparent background (requires png or webp output).',
    )
    image_size: MaiImage27ImageSize | MaiImage27ImageSizePreset = Field(
        default="square_hd",
        description=(
            "The size of the generated image. Each side must be at least 768 pixels and the "
            "total pixel count at most 4,194,304 (2048x2048). Custom sizes are rounded down "
            "to a multiple of 16."
        ),
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="png",
        description="The format of the generated image.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If `True`, the media will be returned as a data URI and the output data "
            "won't be available in the request history."
        ),
    )
    resolution: Literal["1K", "2K"] = Field(
        default="1K",
        description=(
            'Resolution of preset image sizes: "1K" (about 1 megapixel) or "2K" '
            "(each side doubled). Ignored for custom sizes."
        ),
    )

    @model_validator(mode="after")
    def validate_background_output_format(self) -> Self:
        if self.background == "transparent" and self.output_format == "jpeg":
            raise ValueError("transparent background requires png or webp output")
        return self


class MaiImage27TextToImageConfig(MaiImage27Common):
    app_id: Literal["microsoft/mai-image-2.7/text-to-image"]


class MaiImage27FlashTextToImageConfig(MaiImage27Common):
    app_id: Literal["microsoft/mai-image-2.7/flash/text-to-image"]

from __future__ import annotations

from typing import Annotated, ClassVar, Literal

from pydantic import Field, field_validator

from falx.models import BaseFalConfig

MuseImageAspectRatio = Annotated[str, Field(pattern=r"^[1-9][0-9]{0,4}:[1-9][0-9]{0,4}$")]


class MuseImageBaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    prompt: str = Field(
        ...,
        min_length=1,
        description="The text prompt used to generate or edit the image.",
    )
    aspect_ratio: MuseImageAspectRatio | None = Field(
        default=None,
        description=(
            'Any custom output aspect ratio as "width:height", for example "16:9", "5:4", '
            'or "1920:1200". Common presets are "21:9", "16:9", "4:3", "3:2", "1:1", '
            '"2:3", "3:4", "9:16", "9:21". The ratio must be between 1:16 and 16:1, the '
            "range Muse supports. Only the ratio is used: Muse renders it at its own fixed "
            'resolution of roughly 2.5 megapixels, so "1920:1200" and "960:600" both return '
            "the same 1920x1200 image. If omitted, Muse chooses the output dimensions "
            "automatically."
        ),
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=10,
        description="The number of images to generate.",
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="webp",
        description="The format of the generated image.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If true, the image is returned as a data URI and is not persisted in "
            "the request history."
        ),
    )

    @field_validator("aspect_ratio")
    @classmethod
    def validate_aspect_ratio(cls, value: str | None) -> str | None:
        if value is not None:
            width, height = map(int, value.split(":"))
            if width > 16 * height or height > 16 * width:
                raise ValueError("aspect_ratio must be between 1:16 and 16:1")
        return value


class MuseImageTextToImageConfig(MuseImageBaseConfig):
    app_id: Literal["meta/muse-image/text-to-image"]

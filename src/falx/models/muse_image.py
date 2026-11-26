from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

MuseImageAspectRatio = Literal[
    "21:9",
    "16:9",
    "4:3",
    "3:2",
    "1:1",
    "2:3",
    "3:4",
    "9:16",
    "9:21",
]


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
            "The output aspect ratio. If omitted, Muse chooses the output dimensions "
            "automatically based on the request."
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


class MuseImageTextToImageConfig(MuseImageBaseConfig):
    app_id: Literal["meta/muse-image/text-to-image"]

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

GrokImagineImageV20AspectRatio = Literal[
    "2:1",
    "20:9",
    "19.5:9",
    "16:9",
    "4:3",
    "3:2",
    "1:1",
    "2:3",
    "3:4",
    "9:16",
    "9:19.5",
    "9:20",
    "1:2",
]


class GrokImagineImageV20BaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    prompt: str = Field(
        ...,
        max_length=8000,
        description="Text description of the desired image.",
    )
    aspect_ratio: GrokImagineImageV20AspectRatio = Field(
        default="1:1",
        description="Aspect ratio of the generated image.",
    )
    resolution: Literal["1k", "2k"] = Field(
        default="1k",
        description=(
            "Resolution of the generated image. `1k` for standard resolution, "
            "`2k` for high resolution."
        ),
    )
    quality: Literal["low", "medium"] = Field(
        default="medium",
        description="Quality level of the generated image.",
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of images to generate.",
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="jpeg",
        description="The format of the generated image.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If true, the media is returned as a data URI and is not available in "
            "the request history."
        ),
    )


class GrokImagineImageV20TextToImageConfig(GrokImagineImageV20BaseConfig):
    app_id: Literal["xai/grok-imagine-image/v2.0/text-to-image"]

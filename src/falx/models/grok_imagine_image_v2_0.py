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
    "auto",
    "21:9",
    "5:2",
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
        description="Aspect ratio of the generated image. Use auto to let the provider choose.",
    )
    resolution: Literal["1k", "1.5k", "2k"] = Field(
        default="1k",
        description="Resolution of the generated image: 1k, 1.5k, or 2k.",
    )
    quality: Literal["low", "medium", "auto"] = Field(
        default="medium",
        description=(
            "Quality level of the generated image. `auto` lets xAI choose; "
            "it currently uses `low` for generation."
        ),
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of images to generate.",
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="jpeg",
        description="The format of the generated image.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If `True`, the media will be returned as a data URI and the output data "
            "won't be available in the request history."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )


class GrokImagineImageV20TextToImageConfig(GrokImagineImageV20BaseConfig):
    app_id: Literal["xai/grok-imagine-image/v2.0/text-to-image"]

from __future__ import annotations

from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from falx.models import BaseFalConfig

KlingV4ImageAspectRatio = Literal["auto", "16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9"]
KlingV4SeriesAmount = Annotated[int, Field(ge=2, le=10)] | Literal["auto"]


class KlingV4ImageElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frontal_image_url: str = Field(
        ...,
        description=(
            "The frontal image of the element (main view).\n\n"
            "Max file size: 30.0MB, Min width: 300px, Min height: 300px, "
            "Min aspect ratio: 0.40, Max aspect ratio: 2.50, Timeout: 20.0s"
        ),
    )
    reference_image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Additional views of the element from different angles (1-3).",
    )


class KlingV4ImageCommon(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Text prompt for image generation.",
    )
    result_type: Literal["single", "series"] = Field(
        default="single",
        description=(
            "'single' returns independent images; "
            "'series' returns a coherent set of related images."
        ),
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=9,
        description=(
            "Number of independent images to generate (1-9). "
            "Only used when result_type is 'single'."
        ),
    )
    series_amount: KlingV4SeriesAmount = Field(
        default=4,
        description=(
            "Number of images in the series (2-10), or 'auto' to let the model choose. "
            "Only used when result_type is 'series'."
        ),
    )
    resolution: Literal["2K", "4K", "8K"] = Field(
        default="2K",
        description="Output resolution.",
    )
    aspect_ratio: KlingV4ImageAspectRatio = Field(
        default="auto",
        description="Aspect ratio of generated images. 'auto' picks one from the input content.",
    )
    sync_mode: bool = Field(
        default=False,
        description="If `True`, the media will be returned as a data URI.",
    )

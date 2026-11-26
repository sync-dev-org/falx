from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.sam_3_1_common import (
    Sam31BoxPrompt,
    Sam31ImageOutputFormat,
    Sam31PointPrompt,
)


class Sam31ImageRleConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/sam-3-1/image-rle"]
    image_url: str = Field(
        ...,
        description="URL of the image to be segmented.",
    )
    prompt: str = Field(
        default="wheel",
        description="Text prompt for segmentation.",
    )
    point_prompts: list[Sam31PointPrompt] = Field(
        default_factory=list,
        description="List of point prompts.",
    )
    box_prompts: list[Sam31BoxPrompt] = Field(
        default_factory=list,
        description=(
            "Box prompt coordinates (x_min, y_min, x_max, y_max). Multiple boxes supported; "
            "use object_id to group boxes for the same object or leave empty for separate objects."
        ),
    )
    apply_mask: bool = Field(
        default=True,
        description="Apply the mask on the image.",
    )
    sync_mode: bool = Field(
        default=False,
        description="If True, the media will be returned as a data URI.",
    )
    output_format: Sam31ImageOutputFormat = Field(
        default="png",
        description="The format of the generated image.",
    )
    return_multiple_masks: bool = Field(
        default=False,
        description="If True, return multiple generated masks as defined by `max_masks`.",
    )
    max_masks: int = Field(
        default=3,
        ge=1,
        le=32,
        description="Maximum number of masks to return when `return_multiple_masks` is enabled.",
    )
    include_scores: bool = Field(
        default=False,
        description="Whether to include mask confidence scores.",
    )
    include_boxes: bool = Field(
        default=False,
        description="Whether to include bounding boxes for each mask (when available).",
    )

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.sam_3_1_common import (
    Sam31BoxPromptBase,
    Sam31PointPromptBase,
    Sam31VideoOutputType,
)


class Sam31VideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/sam-3-1/video"]
    video_url: str = Field(
        ...,
        description="The URL of the video to be segmented.",
    )
    prompt: str = Field(
        default="",
        description=(
            "Text prompt for segmentation. "
            "Use commas to track multiple objects (e.g., 'person, cloth')."
        ),
    )
    point_prompts: list[Sam31PointPromptBase] = Field(
        default_factory=list,
        description="List of point prompts.",
    )
    box_prompts: list[Sam31BoxPromptBase] = Field(
        default_factory=list,
        description="List of box prompt coordinates (x_min, y_min, x_max, y_max).",
    )
    apply_mask: bool = Field(
        default=True,
        description="Apply the mask on the video.",
    )
    video_output_type: Sam31VideoOutputType = Field(
        default="X264 (.mp4)",
        description="The output type of the generated video.",
    )
    detection_threshold: float = Field(
        default=0.5,
        ge=0.1,
        le=1.0,
        description=(
            "Detection confidence threshold (0.1-1.0). Lower = more detections but less precise."
        ),
    )
    max_num_objects: int = Field(
        default=16,
        ge=1,
        le=128,
        description="Maximum number of objects to track in the video.",
    )

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.sam_3_1_common import (
    Sam31BoxPrompt,
    Sam31PointPrompt,
)


class Sam31VideoRleConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/sam-3-1/video-rle"]
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
    point_prompts: list[Sam31PointPrompt] = Field(
        default_factory=list,
        description="List of point prompts with frame indices.",
    )
    box_prompts: list[Sam31BoxPrompt] = Field(
        default_factory=list,
        description="List of box prompts with optional frame_index.",
    )
    apply_mask: bool = Field(
        default=False,
        description="Apply the mask on the video.",
    )
    detection_threshold: float = Field(
        default=0.5,
        ge=0.01,
        le=1.0,
        description=(
            "Detection confidence threshold (0.01-1.0). "
            "Lower = more detections but less precise. "
            "Defaults: 0.5 for existing, 0.7 for new objects. "
            "Try 0.2-0.3 if text prompts fail."
        ),
    )
    max_num_objects: int = Field(
        default=16,
        ge=1,
        le=128,
        description="Maximum number of objects to track in the video.",
    )
    mask_url: str | None = Field(
        default=None,
        description="Optional initial mask URL.",
    )
    frame_index: int = Field(
        default=0,
        ge=0,
        description="Frame index used for initial interaction when mask_url is provided.",
    )
    boundingbox_zip: bool = Field(
        default=False,
        description="Return per-frame bounding box overlays as a zip archive.",
    )

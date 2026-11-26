from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_v4_common import (
    KlingV4Resolution,
    KlingV4Shot,
    validate_hdr,
    validate_multi_prompt_duration,
)


class KlingV4ImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["kling/v4/image-to-video"]
    prompt: str | None = Field(
        default=None,
        max_length=26000,
        description=(
            "Optional text prompt. Leave empty (and omit multi_prompt) to animate the "
            "frames without one."
        ),
    )
    start_image_url: str = Field(
        ...,
        description=(
            "Image to use as the first frame of the video.\n\nMax file size: 30.0MB, Min "
            "width: 300px, Min height: 300px, Min aspect ratio: 0.40, Max aspect ratio: "
            "2.50, Timeout: 20.0s"
        ),
    )
    middle_image_urls: list[str] | None = Field(
        default=None,
        max_length=8,
        description="Ordered keyframes between the first and last frames (max 8).",
    )
    end_image_url: str | None = Field(
        default=None,
        description="Image to use as the last frame of the video.",
    )
    multi_prompt: list[KlingV4Shot] | None = Field(
        default=None,
        min_length=1,
        description=(
            "Per-shot prompts for multi-shot generation. The video duration is the sum of"
            " the shot durations."
        ),
    )
    duration: int = Field(
        default=5,
        ge=3,
        le=30,
        description="Video duration in seconds (3-30).",
    )
    resolution: KlingV4Resolution = Field(
        default="1080p",
        description="Output resolution.",
    )
    hdr: bool = Field(
        default=False,
        description=(
            "Whether to output 10-bit HDR instead of SDR. Supported at 1080p and 4k only,"
            " and billed on top of the base rate."
        ),
    )

    @model_validator(mode="after")
    def validate_kling_v4_constraints(self) -> Self:
        validate_hdr(self.resolution, self.hdr)
        validate_multi_prompt_duration(self.multi_prompt)
        return self

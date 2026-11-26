from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.vidu_q3_common import (
    VIDU_Q3_ASPECT_RATIO_DESCRIPTION,
    VIDU_Q3_DURATION_DESCRIPTION,
    VIDU_Q3_RESOLUTION_DESCRIPTION,
    ViduQ3AspectRatio,
    ViduQ3Resolution,
)


class ViduQ3ReferenceToVideoBase(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        max_length=2000,
        description="Text prompt for video generation, max 2000 characters.",
    )
    reference_image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=4,
        description="URLs of 1 to 4 reference images used to keep subjects or scenes consistent.",
    )
    duration: int = Field(
        default=5,
        ge=1,
        le=16,
        description=VIDU_Q3_DURATION_DESCRIPTION,
    )
    seed: int | None = Field(
        default=None,
        description="Random seed for reproducibility. If None, a random seed is chosen.",
    )
    aspect_ratio: ViduQ3AspectRatio = Field(
        default="16:9",
        description=VIDU_Q3_ASPECT_RATIO_DESCRIPTION,
    )
    resolution: ViduQ3Resolution = Field(
        default="720p",
        description=VIDU_Q3_RESOLUTION_DESCRIPTION,
    )
    audio: bool = Field(
        default=True,
        description=(
            "Whether to use direct audio-video generation. When true, outputs video with sound."
        ),
    )


class ViduQ3ReferenceToVideoConfig(ViduQ3ReferenceToVideoBase):
    app_id: Literal["fal-ai/vidu/q3/reference-to-video"]

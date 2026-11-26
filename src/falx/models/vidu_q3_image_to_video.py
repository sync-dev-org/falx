from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.vidu_q3_common import (
    VIDU_Q3_DURATION_DESCRIPTION,
    VIDU_Q3_RESOLUTION_DESCRIPTION,
    ViduQ3Resolution,
)


class ViduQ3ImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["fal-ai/vidu/q3/image-to-video"]
    prompt: str = Field(
        default="",
        max_length=2000,
        description="Text prompt for video generation, max 2000 characters.",
    )
    image_url: str = Field(
        ...,
        description="URL or base64 image to use as the starting frame.",
    )
    end_image_url: str | None = Field(
        default=None,
        description=(
            "URL of the image to use as the ending frame. When provided, generates "
            "a transition video between start and end frames."
        ),
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
    resolution: ViduQ3Resolution = Field(
        default="720p",
        description=(
            f"{VIDU_Q3_RESOLUTION_DESCRIPTION} 360p is not available when "
            "end_image_url is provided."
        ),
    )
    audio: bool = Field(
        default=True,
        description=(
            "Whether to use direct audio-video generation. When true, outputs video "
            "with sound, including dialogue and sound effects."
        ),
    )

    @model_validator(mode="after")
    def validate_transition_resolution(self) -> Self:
        if self.end_image_url is not None and self.resolution == "360p":
            raise ValueError("360p is not available when end_image_url is provided")
        return self

from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_o3_common import (
    KlingO3ImageElementInput,
    validate_reference_indices,
)


class KlingVideoO3ProVideoToVideoEditConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/pro/video-to-video/edit"]
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Disabling safety checks requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )
    prompt: str = Field(
        ...,
        max_length=2500,
        description="Text prompt for video generation. Reference video as @Video1.",
    )
    video_url: str = Field(
        ...,
        description=(
            "Reference video URL. Only .mp4/.mov formats, 3-10s duration, "
            "720-2160px resolution, max 200MB."
        ),
    )
    shot_type: Literal["customize"] = Field(
        default="customize",
        description="The type of multi-shot video generation.",
    )
    elements: list[KlingO3ImageElementInput] | None = Field(
        default=None,
        description=(
            "Elements (characters/objects) to include. Reference in prompt as @Element1, @Element2."
        ),
    )
    keep_audio: bool = Field(
        default=True,
        description="Whether to keep the original audio from the reference video.",
    )
    image_urls: list[str] | None = Field(
        default=None,
        description=(
            "Reference images for style/appearance. Reference in prompt as @Image1, "
            "@Image2, etc. Maximum 4 total (elements + reference images) when using video."
        ),
    )

    @model_validator(mode="after")
    def validate_kling_o3_edit_constraints(self) -> Self:
        element_count = len(self.elements or [])
        image_count = len(self.image_urls or [])
        if element_count + image_count > 4:
            raise ValueError("Maximum 4 total elements + image_urls is allowed")

        validate_reference_indices(
            self.prompt,
            None,
            element_count=element_count,
            image_count=image_count,
        )
        return self

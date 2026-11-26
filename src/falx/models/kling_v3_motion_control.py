from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from falx.models import BaseFalConfig


class KlingV3ImageElementInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frontal_image_url: str | None = Field(
        default=None,
        description=("Frontal facial element image URL used for identity preservation binding."),
    )
    reference_image_urls: list[str] | None = Field(
        default=None,
        min_length=1,
        max_length=3,
        description=(
            "Additional facial element reference image URLs used for identity preservation binding."
        ),
    )

    @model_validator(mode="after")
    def validate_at_least_one_image(self) -> Self:
        if self.frontal_image_url is None and self.reference_image_urls is None:
            raise ValueError("frontal_image_url or reference_image_urls is required")
        return self


class KlingVideoV3ProMotionControlConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/v3/pro/motion-control"]
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Disabling safety checks requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )
    prompt: str | None = Field(
        default=None,
        max_length=2500,
        description="Optional text prompt for video generation.",
    )
    image_url: str = Field(
        ...,
        description=(
            "Reference image URL that provides the characters, backgrounds, and other "
            "elements for the generated video."
        ),
    )
    video_url: str = Field(
        ...,
        description=(
            "Reference video URL whose character actions should be followed. Duration "
            "limit depends on character_orientation: image allows up to 10s, video up "
            "to 30s."
        ),
    )
    character_orientation: Literal["image", "video"] = Field(
        ...,
        description=(
            "Controls how the reference video's motion is applied to the output "
            "character. image matches the reference image orientation and is better "
            "for camera movement; video matches the reference video orientation and "
            "is better for complex motion."
        ),
    )
    elements: list[KlingV3ImageElementInput] | None = Field(
        default=None,
        max_length=1,
        description=(
            "Optional facial consistency element to bind identity in the generated "
            "video. Reference it in the prompt as @Element1; supported only when "
            "character_orientation is video."
        ),
    )
    keep_original_sound: bool = Field(
        default=True,
        description="Whether to keep the original sound from the reference video.",
    )

    @model_validator(mode="after")
    def validate_elements_require_video_orientation(self) -> Self:
        if self.elements is not None and self.character_orientation != "video":
            raise ValueError("elements require character_orientation='video'")
        return self

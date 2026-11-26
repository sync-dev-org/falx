from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_o3_common import (
    KlingO3Duration,
    KlingO3MultiPromptElement,
    KlingO3ShotType,
    validate_prompt_choice,
)


class KlingVideoO3ProImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/pro/image-to-video"]
    prompt: str | None = Field(
        default=None,
        max_length=2500,
        description=(
            "Text prompt for video generation. Either prompt or multi_prompt must "
            "be provided, but not both."
        ),
    )
    image_url: str = Field(
        ...,
        description="URL of the start frame image.",
    )
    shot_type: KlingO3ShotType = Field(
        default="customize",
        description=(
            "The type of multi-shot video generation. intelligent lets the model "
            "automatically determine shot structure."
        ),
    )
    end_image_url: str | None = Field(
        default=None,
        description="URL of the end frame image (optional).",
    )
    multi_prompt: list[KlingO3MultiPromptElement] | None = Field(
        default=None,
        description="List of prompts for multi-shot video generation.",
    )
    duration: KlingO3Duration = Field(
        default="5",
        description=(
            "Video duration in seconds. "
            "Allowed values: '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', "
            "'13', '14', '15' (string)."
        ),
    )
    generate_audio: bool = Field(
        default=False,
        description="Whether to generate native audio for the video.",
    )

    @model_validator(mode="after")
    def validate_kling_o3_i2v_constraints(self) -> Self:
        validate_prompt_choice(self.prompt, self.multi_prompt)
        return self

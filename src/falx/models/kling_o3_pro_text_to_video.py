from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_o3_common import (
    KlingO3AspectRatio,
    KlingO3Duration,
    KlingO3MultiPromptElement,
    KlingO3ShotType,
    validate_prompt_choice,
)


class KlingVideoO3ProTextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/pro/text-to-video"]
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
        description="Text prompt for video generation. Required unless multi_prompt is provided.",
    )
    aspect_ratio: KlingO3AspectRatio = Field(
        default="16:9",
        description="Aspect ratio of the generated video.",
    )
    shot_type: KlingO3ShotType = Field(
        default="customize",
        description=(
            "The type of multi-shot video generation. intelligent lets the model "
            "automatically determine shot structure."
        ),
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
    multi_prompt: list[KlingO3MultiPromptElement] | None = Field(
        default=None,
        description="List of prompts for multi-shot video generation.",
    )

    @model_validator(mode="after")
    def validate_kling_o3_t2v_constraints(self) -> Self:
        validate_prompt_choice(self.prompt, self.multi_prompt)
        return self

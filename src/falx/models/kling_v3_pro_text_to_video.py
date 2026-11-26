from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_v3_common import (
    KlingV3AspectRatio,
    KlingV3Duration,
    KlingV3MultiPromptElement,
    KlingV3ShotType,
    validate_prompt_choice,
)


class KlingVideoV3ProTextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None
    schema_example_parameters: ClassVar[dict[str, Any]] = {"prompt": "<your prompt here>"}

    app_id: Literal["fal-ai/kling-video/v3/pro/text-to-video"]
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
        description=(
            "Text prompt for video generation. Either prompt or multi_prompt must "
            "be provided, but not both."
        ),
    )
    duration: KlingV3Duration = Field(
        default="5",
        description=(
            "The duration of the generated video in seconds. "
            "Allowed values: '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', "
            "'13', '14', '15' (string)."
        ),
    )
    multi_prompt: list[KlingV3MultiPromptElement] | None = Field(
        default=None,
        description=(
            "List of prompts for multi-shot video generation. If provided, it divides "
            "the video into multiple shots with specified prompts and durations."
        ),
    )
    generate_audio: bool = Field(
        default=True,
        description=(
            "Whether to generate native audio for the video. Supports Chinese and "
            "English voice output."
        ),
    )
    shot_type: KlingV3ShotType = Field(
        default="customize",
        description=(
            "The type of multi-shot video generation. intelligent lets the model "
            "automatically determine shot structure."
        ),
    )
    aspect_ratio: KlingV3AspectRatio = Field(
        default="16:9",
        description="The aspect ratio of the generated video frame.",
    )
    negative_prompt: str = Field(
        default="blur, distort, and low quality",
        max_length=2500,
        description="Negative prompt for video generation.",
    )
    cfg_scale: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description="The CFG scale controls how closely the model follows the prompt.",
    )

    @model_validator(mode="after")
    def validate_kling_v3_t2v_constraints(self) -> Self:
        validate_prompt_choice(self.prompt, self.multi_prompt)
        return self

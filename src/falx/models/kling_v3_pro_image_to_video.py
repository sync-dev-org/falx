from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_v3_common import (
    KlingV3ComboElementInput,
    KlingV3Duration,
    KlingV3MultiPromptElement,
    KlingV3ShotType,
    validate_combo_elements,
    validate_prompt_choice,
)


class KlingVideoV3ProImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/v3/pro/image-to-video"]
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
    multi_prompt: list[KlingV3MultiPromptElement] | None = Field(
        default=None,
        description="List of prompts for multi-shot video generation.",
    )
    start_image_url: str = Field(
        ...,
        description="URL of the image to be used for the video.",
    )
    duration: KlingV3Duration = Field(
        default="5",
        description=(
            "The duration of the generated video in seconds. "
            "Allowed values: '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', "
            "'13', '14', '15' (string)."
        ),
    )
    generate_audio: bool = Field(
        default=True,
        description=(
            "Whether to generate native audio for the video. Supports Chinese and "
            "English voice output."
        ),
    )
    end_image_url: str | None = Field(
        default=None,
        description="URL of the image to be used for the end of the video.",
    )
    elements: list[KlingV3ComboElementInput] | None = Field(
        default=None,
        description=(
            "Elements to include in the video. Each element is either an image set "
            "or a video and may be referenced as @Element1, @Element2, etc."
        ),
    )
    shot_type: KlingV3ShotType = Field(
        default="customize",
        description=(
            "The type of multi-shot video generation. intelligent lets the model "
            "automatically determine shot structure."
        ),
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
    def validate_kling_v3_i2v_constraints(self) -> Self:
        validate_prompt_choice(self.prompt, self.multi_prompt)
        validate_combo_elements(self.prompt, self.multi_prompt, self.elements)
        return self

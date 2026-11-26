from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_o3_common import (
    KlingO3AspectRatio,
    KlingO3ComboElementInput,
    KlingO3Duration,
    KlingO3MultiPromptElement,
    KlingO3ShotType,
    validate_combo_video_count,
    validate_prompt_choice,
    validate_reference_indices,
)


class KlingVideoO3ProReferenceToVideoConfig(BaseFalConfig):
    max_total_references_when_using_video: ClassVar[int] = 4
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/pro/reference-to-video"]
    prompt: str | None = Field(
        default=None,
        max_length=2500,
        description=(
            "Text prompt for video generation. Either prompt or multi_prompt must "
            "be provided, but not both."
        ),
    )
    start_image_url: str | None = Field(
        default=None,
        description="Image to use as the first frame of the video.",
    )
    duration: KlingO3Duration = Field(
        default="5",
        description=(
            "Video duration in seconds. "
            "Allowed values: '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', "
            "'13', '14', '15' (string)."
        ),
    )
    end_image_url: str | None = Field(
        default=None,
        description="Image to use as the last frame of the video.",
    )
    generate_audio: bool = Field(
        default=False,
        description="Whether to generate native audio for the video.",
    )
    aspect_ratio: KlingO3AspectRatio = Field(
        default="16:9",
        description="The aspect ratio of the generated video frame.",
    )
    shot_type: KlingO3ShotType = Field(
        default="customize",
        description=(
            "The type of multi-shot video generation. intelligent lets the model "
            "automatically determine shot structure."
        ),
    )
    elements: list[KlingO3ComboElementInput] | None = Field(
        default=None,
        description=(
            "Elements (characters/objects) to include. Reference in prompt as @Element1, @Element2."
        ),
    )
    image_urls: list[str] | None = Field(
        default=None,
        description=(
            "Reference images for style/appearance. Reference in prompt as @Image1, "
            "@Image2, etc. Maximum 4 total (elements + reference images) when using video."
        ),
    )
    multi_prompt: list[KlingO3MultiPromptElement] | None = Field(
        default=None,
        description="List of prompts for multi-shot video generation.",
    )

    @model_validator(mode="after")
    def validate_kling_o3_r2v_constraints(self) -> Self:
        validate_prompt_choice(self.prompt, self.multi_prompt)

        element_count = len(self.elements or [])
        image_count = len(self.image_urls or [])
        video_element_count = validate_combo_video_count(self.elements)

        if video_element_count and (
            element_count + image_count > self.max_total_references_when_using_video
        ):
            raise ValueError(
                f"Maximum {self.max_total_references_when_using_video} total "
                "elements + image_urls is allowed when using video"
            )

        validate_reference_indices(
            self.prompt,
            self.multi_prompt,
            element_count=element_count,
            image_count=image_count,
        )
        return self

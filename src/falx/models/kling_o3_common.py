from __future__ import annotations

import re
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

KlingO3Duration = Literal[
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
]
KlingO3ShotDuration = Literal[
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
]
KlingO3AspectRatio = Literal["16:9", "9:16", "1:1"]
KlingO3ShotType = Literal["customize", "intelligent"]

_ELEMENT_REFERENCE_PATTERN = re.compile(r"@Element(\d+)")
_IMAGE_REFERENCE_PATTERN = re.compile(r"@Image(\d+)")


class KlingO3MultiPromptElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(..., description="The prompt for this shot.")
    duration: KlingO3ShotDuration = Field(
        default="5",
        description=(
            "The duration of this shot in seconds. "
            "Allowed values: '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', "
            "'11', '12', '13', '14', '15' (string)."
        ),
    )


class KlingO3ComboElementInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference_image_urls: list[str] | None = Field(
        default=None,
        min_length=1,
        max_length=3,
        description=(
            "Additional reference images from different angles. 1-3 images supported. "
            "At least one image is required."
        ),
    )
    video_url: str | None = Field(
        default=None,
        description=(
            "The video URL of the element. A request can only have one element with a video."
        ),
    )
    voice_id: str | None = Field(
        default=None,
        description=(
            "Voice ID bound to this element. Voice binding is supported only for "
            "video elements and cannot be used with image elements."
        ),
    )
    frontal_image_url: str | None = Field(
        default=None,
        description="The frontal image of the element (main view).",
    )

    @model_validator(mode="after")
    def validate_element_kind(self) -> Self:
        has_image_fields = (
            self.frontal_image_url is not None or self.reference_image_urls is not None
        )
        has_video = self.video_url is not None

        if not has_image_fields and not has_video:
            raise ValueError("frontal_image_url or reference_image_urls or video_url is required")
        if has_image_fields and has_video:
            raise ValueError("elements must use either image fields or video_url")
        if self.voice_id is not None and not has_video:
            raise ValueError("voice_id requires video_url")
        return self


class KlingO3ImageElementInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference_image_urls: list[str] | None = Field(
        default=None,
        min_length=1,
        max_length=3,
        description=(
            "Additional reference images from different angles. 1-3 images supported. "
            "At least one image is required."
        ),
    )
    frontal_image_url: str | None = Field(
        default=None,
        description="The frontal image of the element (main view).",
    )

    @model_validator(mode="after")
    def validate_at_least_one_image(self) -> Self:
        if self.frontal_image_url is None and self.reference_image_urls is None:
            raise ValueError("frontal_image_url or reference_image_urls is required")
        return self


def validate_prompt_choice(
    prompt: str | None,
    multi_prompt: list[KlingO3MultiPromptElement] | None,
) -> None:
    if prompt is None and multi_prompt is None:
        raise ValueError("prompt or multi_prompt is required")
    if prompt is not None and multi_prompt is not None:
        raise ValueError("provide prompt or multi_prompt, not both")


def validate_reference_indices(
    prompt: str | None,
    multi_prompt: list[KlingO3MultiPromptElement] | None,
    element_count: int,
    image_count: int,
) -> None:
    prompts = []
    if prompt is not None:
        prompts.append(prompt)
    if multi_prompt is not None:
        prompts.extend(element.prompt for element in multi_prompt)

    for prompt_text in prompts:
        for match in _ELEMENT_REFERENCE_PATTERN.finditer(prompt_text):
            element_index = int(match.group(1))
            if element_index < 1 or element_index > element_count:
                raise ValueError(f"@Element{element_index} is outside the elements range")

        for match in _IMAGE_REFERENCE_PATTERN.finditer(prompt_text):
            image_index = int(match.group(1))
            if image_index < 1 or image_index > image_count:
                raise ValueError(f"@Image{image_index} is outside the image_urls range")


def validate_combo_video_count(elements: list[KlingO3ComboElementInput] | None) -> int:
    if elements is None:
        return 0

    video_element_count = sum(1 for element in elements if element.video_url is not None)
    if video_element_count > 1:
        raise ValueError("a request can only have one element with a video")
    return video_element_count

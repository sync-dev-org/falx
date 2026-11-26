from __future__ import annotations

import re
from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig

_IMAGE_REFERENCE_PATTERN = re.compile(r"@Image(\d+)\b")


class HappyHorseVideoEditConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["alibaba/happy-horse/video-edit"]
    video_url: str = Field(
        ...,
        description=("URL of the source video to edit. Supported formats are MP4 and MOV."),
    )
    prompt: str = Field(
        ...,
        max_length=2500,
        description=(
            "Text prompt describing the desired edit. Refer to supplied reference "
            "images as @Image1, @Image2, and so on."
        ),
    )
    reference_image_urls: list[str] | None = Field(
        default=None,
        max_length=5,
        description="Optional reference images used to guide the edit.",
    )
    resolution: Literal["720p", "1080p"] = Field(
        default="1080p",
        description="Output video resolution tier.",
    )
    audio_setting: Literal["auto", "origin"] = Field(
        default="auto",
        description=(
            "Audio handling. auto lets the model decide whether to regenerate audio; "
            "origin preserves the original input audio."
        ),
    )
    seed: int | None = Field(
        default=None,
        ge=0,
        le=2_147_483_647,
        description="Random seed for reproducibility.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Enable content moderation for input and output.",
    )

    @model_validator(mode="after")
    def validate_prompt_image_references(self) -> Self:
        reference_count = len(self.reference_image_urls or [])

        for match in _IMAGE_REFERENCE_PATTERN.finditer(self.prompt):
            image_index = int(match.group(1))
            if image_index < 1 or image_index > reference_count:
                raise ValueError(
                    f"prompt references @Image{image_index}, "
                    f"but reference_image_urls has {reference_count} images"
                )
        return self

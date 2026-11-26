from __future__ import annotations

import re
from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig

_CHARACTER_REFERENCE_PATTERN = re.compile(r"\bcharacter(\d+)\b")


class HappyHorseReferenceToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["alibaba/happy-horse/reference-to-video"]
    prompt: str = Field(
        ...,
        max_length=2500,
        description=(
            "Text prompt describing the desired video. Refer to subjects from "
            "image_urls as character1, character2, and so on."
        ),
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=9,
        description=(
            "Reference images for subject consistency. The order matches character1 "
            "through character9 prompt references."
        ),
    )
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4"] = Field(
        default="16:9",
        description="Aspect ratio of the generated video.",
    )
    resolution: Literal["720p", "1080p"] = Field(
        default="1080p",
        description="Output video resolution tier.",
    )
    duration: Literal[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] = Field(
        default=5,
        description=(
            "Output video duration in seconds. "
            "Allowed values: 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 (int)."
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
    def validate_prompt_character_references(self) -> Self:
        image_count = len(self.image_urls)

        for match in _CHARACTER_REFERENCE_PATTERN.finditer(self.prompt):
            character_index = int(match.group(1))
            if character_index < 1 or character_index > image_count:
                raise ValueError(
                    f"prompt references character{character_index}, "
                    f"but image_urls has {image_count} images"
                )
        return self

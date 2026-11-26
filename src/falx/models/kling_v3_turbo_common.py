from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_v3_common import KlingV3Duration, KlingV3MultiPromptElement


class KlingV3TurboConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    prompt: str | None = Field(
        default=None,
        max_length=3072,
        description=(
            "Text prompt to generate the video with. For best results keep the prompt "
            "under 2500 characters. Mutually exclusive with `multi_prompt`."
        ),
    )
    multi_prompt: list[KlingV3MultiPromptElement] | None = Field(
        default=None,
        min_length=1,
        max_length=6,
        description=(
            "Multi-shot storyboard (1-6 shots). Each shot has its own prompt and duration; "
            "the total duration must not exceed 15s. Mutually exclusive with `prompt`."
        ),
    )
    duration: KlingV3Duration = Field(
        default="5",
        description="Video length in seconds.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Disabling safety checks requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )

    @model_validator(mode="after")
    def validate_kling_v3_turbo_storyboard(self) -> Self:
        if self.prompt is not None and self.multi_prompt is not None:
            raise ValueError("prompt and multi_prompt are mutually exclusive")
        if (
            self.multi_prompt is not None
            and sum(int(shot.duration) for shot in self.multi_prompt) > 15
        ):
            raise ValueError("multi_prompt total duration must not exceed 15 seconds")
        return self

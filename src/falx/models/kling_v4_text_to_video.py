from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_v4_common import (
    KlingV4AspectRatio,
    KlingV4Resolution,
    KlingV4Shot,
    validate_hdr,
    validate_multi_prompt_duration,
    validate_prompt_input,
)


class KlingV4TextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None
    schema_example_parameters: ClassVar[dict[str, Any]] = {"prompt": "<your prompt here>"}

    app_id: Literal["kling/v4/text-to-video"]
    prompt: str | None = Field(
        default=None,
        max_length=26000,
        description="Text prompt. Either prompt or multi_prompt must be provided.",
    )
    multi_prompt: list[KlingV4Shot] | None = Field(
        default=None,
        min_length=1,
        description=(
            "Per-shot prompts for multi-shot generation. The video duration is the sum of"
            " the shot durations."
        ),
    )
    duration: int = Field(
        default=5,
        ge=3,
        le=30,
        description="Video duration in seconds (3-30).",
    )
    resolution: KlingV4Resolution = Field(
        default="1080p",
        description="Output resolution.",
    )
    hdr: bool = Field(
        default=False,
        description=(
            "Whether to output 10-bit HDR instead of SDR. Supported at 1080p and 4k only,"
            " and billed on top of the base rate."
        ),
    )
    aspect_ratio: KlingV4AspectRatio = Field(
        default="16:9",
        description="Aspect ratio of the generated video.",
    )

    @model_validator(mode="after")
    def validate_kling_v4_constraints(self) -> Self:
        validate_hdr(self.resolution, self.hdr)
        validate_multi_prompt_duration(self.multi_prompt)
        validate_prompt_input(self.prompt, self.multi_prompt)
        return self

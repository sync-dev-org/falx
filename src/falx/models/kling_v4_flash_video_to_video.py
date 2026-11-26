from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_v4_common import (
    KlingV4FlashElement,
    validate_reference_limits,
)


class KlingV4FlashVideoToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["kling/v4/flash/video-to-video"]
    prompt: str = Field(
        ...,
        max_length=26000,
        description="Edit instruction. Reference the source video as @Video1.",
    )
    video_url: str = Field(
        ...,
        description=(
            "The video to edit (3-20s), referenced as @Video1.\n\nMax file size: 300.0MB, "
            "Min width: 700px, Min height: 700px, Max width: 4553px, Max height: 4553px, "
            "Min aspect ratio: 0.40, Max aspect ratio: 2.50, Min duration: 3.0s, Max "
            "duration: 20.05s, Min FPS: 23.9, Max FPS: 60.05, Timeout: 30.0s"
        ),
    )
    image_urls: list[str] | None = Field(
        default=None,
        max_length=10,
        description="Reference images, referenced as @Image1, @Image2, ... (max 10).",
    )
    video_urls: list[str] | None = Field(
        default=None,
        max_length=4,
        description=(
            "Reference videos, referenced as @Video2, @Video3, ... (max 4). The source, "
            "reference and element videos must total at most 20s."
        ),
    )
    elements: list[KlingV4FlashElement] | None = Field(
        default=None,
        max_length=7,
        description=(
            "Characters/objects, referenced as @Element1, @Element2, ... (max 7). Up to 3"
            " may be video elements. Flash does not accept voices."
        ),
    )
    keep_audio: bool = Field(
        default=False,
        description=(
            "Keep the original audio of the source video instead of generating new audio."
            " Cannot be combined with voices."
        ),
    )
    duration: int | None = Field(
        default=None,
        ge=3,
        le=20,
        description="Output duration in seconds (3-20). Defaults to the source video's length.",
    )
    resolution: Literal["720p"] = Field(
        default="720p",
        description="Output resolution. Flash is 720p only.",
    )

    @model_validator(mode="after")
    def validate_kling_v4_flash_constraints(self) -> Self:
        validate_reference_limits(
            self.elements,
            self.image_urls,
            keep_audio=self.keep_audio,
        )
        return self

from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_v4_common import (
    KlingV4Element,
    KlingV4ReferenceAspectRatio,
    KlingV4Resolution,
    validate_hdr,
    validate_reference_limits,
)


class KlingV4VideoToVideoEditConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["kling/v4/video-to-video/edit"]
    prompt: str = Field(
        ...,
        max_length=26000,
        description="Edit instruction. Reference the source video as @Video1.",
    )
    video_url: str = Field(
        ...,
        description=(
            "The video to edit (3-30s), referenced as @Video1.\n\nMax file size: 300.0MB, "
            "Min width: 700px, Min height: 700px, Max width: 4553px, Max height: 4553px, "
            "Min aspect ratio: 0.40, Max aspect ratio: 2.50, Min duration: 3.0s, Max "
            "duration: 30.05s, Min FPS: 23.9, Max FPS: 60.05, Timeout: 30.0s"
        ),
    )
    image_urls: list[str] | None = Field(
        default=None,
        max_length=10,
        description="Reference images, referenced as @Image1, @Image2, ...",
    )
    video_urls: list[str] | None = Field(
        default=None,
        max_length=4,
        description=(
            "Reference videos, referenced as @Video2, @Video3, ... (max 4). The source, "
            "reference and element videos must total at most 30s."
        ),
    )
    elements: list[KlingV4Element] | None = Field(
        default=None,
        max_length=7,
        description=(
            "Characters/objects, referenced as @Element1, @Element2, ... (max 7). Up to 3"
            " elements may carry a voice_id and up to 3 may be video elements."
        ),
    )
    voice_ids: list[str] | None = Field(
        default=None,
        max_length=3,
        description=(
            "Voices referenced in the prompt as @Voice1, @Voice2, ... (max 3, including "
            "voices bound to elements). Create one with "
            "https://fal.ai/models/fal-ai/kling-video/create-voice"
        ),
    )
    start_image_url: str | None = Field(
        default=None,
        description=(
            "Optional image to use as the first frame. Counts toward the image reference limit."
        ),
    )
    middle_image_urls: list[str] | None = Field(
        default=None,
        max_length=8,
        description=(
            "Optional ordered keyframes between the first and last frames (max 8). Count "
            "toward the image reference limit."
        ),
    )
    end_image_url: str | None = Field(
        default=None,
        description=(
            "Optional image to use as the last frame. Counts toward the image reference limit."
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
        le=30,
        description="Output duration in seconds (3-30). Defaults to the source video's length.",
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
    aspect_ratio: KlingV4ReferenceAspectRatio | None = Field(
        default=None,
        description=(
            "Aspect ratio of the edited video. 'auto' adapts it to the inputs. Omit to "
            "follow the source video."
        ),
    )

    @model_validator(mode="after")
    def validate_kling_v4_constraints(self) -> Self:
        validate_hdr(self.resolution, self.hdr)
        validate_reference_limits(
            self.elements,
            self.image_urls,
            start_image_url=self.start_image_url,
            middle_image_urls=self.middle_image_urls,
            end_image_url=self.end_image_url,
            voice_ids=self.voice_ids,
            keep_audio=self.keep_audio,
        )
        return self

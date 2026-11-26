from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_v4_common import (
    KlingV4Element,
    KlingV4ReferenceAspectRatio,
    KlingV4Resolution,
    KlingV4Shot,
    validate_hdr,
    validate_multi_prompt_duration,
    validate_prompt_input,
    validate_reference_limits,
)


class KlingV4ReferenceToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["kling/v4/reference-to-video"]
    prompt: str | None = Field(
        default=None,
        max_length=26000,
        description=(
            "Text prompt. Reference inputs as @Image1, @Video1, @Element1, etc. Either "
            "prompt or multi_prompt must be provided."
        ),
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
    image_urls: list[str] | None = Field(
        default=None,
        max_length=10,
        description="Reference images, referenced as @Image1, @Image2, ... (max 10).",
    )
    video_urls: list[str] | None = Field(
        default=None,
        max_length=5,
        description=(
            "Reference videos (3-30s each, 30s combined with element videos), referenced "
            "as @Video1, @Video2, ... (max 5)."
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
    keep_audio: bool = Field(
        default=False,
        description=(
            "Keep the original audio of the first reference video (@Video1) instead of "
            "generating new audio. Cannot be combined with voices."
        ),
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
    aspect_ratio: KlingV4ReferenceAspectRatio = Field(
        default="16:9",
        description="Aspect ratio of the generated video. 'auto' adapts it to the references.",
    )

    @model_validator(mode="after")
    def validate_kling_v4_constraints(self) -> Self:
        validate_hdr(self.resolution, self.hdr)
        validate_multi_prompt_duration(self.multi_prompt)
        validate_prompt_input(self.prompt, self.multi_prompt)
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

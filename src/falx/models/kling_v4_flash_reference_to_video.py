from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.kling_v4_common import (
    KlingV4FlashElement,
    KlingV4ReferenceAspectRatio,
    validate_reference_limits,
)


class KlingV4FlashReferenceToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["kling/v4/flash/reference-to-video"]
    prompt: str = Field(
        ...,
        max_length=26000,
        description="Text prompt. Reference inputs as @Image1, @Video1, @Element1, etc.",
    )
    duration: int = Field(
        default=5,
        ge=3,
        le=20,
        description="Video duration in seconds (3-20).",
    )
    start_image_url: str | None = Field(
        default=None,
        description=(
            "Optional image to use as the first frame. Counts toward the image reference limit."
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
            "Reference videos (3-20s each, 20s combined with element videos), referenced "
            "as @Video1, @Video2, ... (max 5)."
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
            "Keep the original audio of the first reference video (@Video1) instead of "
            "generating new audio. Cannot be combined with voices."
        ),
    )
    resolution: Literal["720p"] = Field(
        default="720p",
        description="Output resolution. Flash is 720p only.",
    )
    aspect_ratio: KlingV4ReferenceAspectRatio = Field(
        default="16:9",
        description="Aspect ratio of the generated video. 'auto' adapts it to the references.",
    )

    @model_validator(mode="after")
    def validate_kling_v4_flash_constraints(self) -> Self:
        validate_reference_limits(
            self.elements,
            self.image_urls,
            start_image_url=self.start_image_url,
            keep_audio=self.keep_audio,
        )
        return self

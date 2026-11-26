from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class MinimaxH3MaxReferenceToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max/reference-to-video"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50_000,
        description=(
            "Text prompt for video generation. Refer to reference assets by their "
            "modality and order in the reference lists: Image 1, Image 2, Video 1, "
            "Audio 1, and so on."
        ),
    )
    duration: int = Field(
        default=5,
        ge=5,
        le=15,
        description="The duration of the video in seconds.",
    )
    resolution: Literal["480P", "768P", "1080P"] = Field(
        default="768P",
        description=(
            "The native generation resolution, or 1080P latent refinement from a "
            "native 768P source."
        ),
    )
    seed: int | None = Field(
        default=None,
        description="Random seed. A random seed is selected when omitted.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="If set to true, the safety checker will be enabled.",
    )
    sync_mode: bool = Field(
        default=False,
        description="Return the generated video as base64 instead of a CDN URL.",
    )
    prompt_expansion_mode: str = Field(
        ...,
        description=(
            "How much effort to spend rewriting the prompt before generation. "
            "'balanced' returns in about a second. 'quality' spends up to ~30s on a "
            "richer prompt."
        ),
        json_schema_extra={"default": "balanced"},
    )
    aspect_ratio: Literal[
        "adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"
    ] = Field(
        default="adaptive",
        description="The aspect ratio of the generated video.",
    )
    reference_image_urls: list[str] = Field(
        default_factory=list,
        max_length=9,
        description=(
            "URLs of subject/style reference images, referenced in the prompt as Image "
            "1, Image 2, and so on. Reference images, videos, and audio clips must add "
            "up to at most 12 files."
        ),
    )
    reference_video_urls: list[str] = Field(
        default_factory=list,
        max_length=3,
        description=(
            "URLs of motion/reference video clips (2-15 seconds each, combined duration "
            "at most 15 seconds), referenced in the prompt as Video 1, Video 2, and so "
            "on. Reference images, videos, and audio clips must add up to at most 12 "
            "files."
        ),
    )
    reference_audio_urls: list[str] = Field(
        default_factory=list,
        max_length=3,
        description=(
            "URLs of reference audio clips (2-15 seconds each, combined duration at "
            "most 15 seconds), referenced in the prompt as Audio 1, Audio 2, and so on. "
            "Audio cannot be the only reference input; provide at least one reference "
            "image or video with it. Reference images, videos, and audio clips must add "
            "up to at most 12 files."
        ),
    )

    @model_validator(mode="after")
    def validate_reference_file_constraints(self) -> Self:
        reference_count = (
            len(self.reference_image_urls)
            + len(self.reference_video_urls)
            + len(self.reference_audio_urls)
        )
        if reference_count > 12:
            raise ValueError(
                "total files across reference_image_urls, reference_video_urls, and "
                "reference_audio_urls must be <= 12"
            )
        if self.reference_audio_urls and not (
            self.reference_image_urls or self.reference_video_urls
        ):
            raise ValueError(
                "reference_audio_urls require reference_image_urls or "
                "reference_video_urls"
            )
        return self

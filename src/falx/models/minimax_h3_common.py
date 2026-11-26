from __future__ import annotations

from typing import Annotated, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class MinimaxH3BaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50_000,
        description="Text prompt for video generation",
    )
    duration: int = Field(
        default=5,
        ge=5,
        le=15,
        description="The duration of the video in seconds.",
    )
    resolution: Literal["480P", "768P", "2K", "4K"] = Field(
        default="2K",
        description=(
            "The resolution of the generated video. 480P and 768P are native "
            "generation modes; 2K and 4K upscale a 768P base result."
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
    prompt_expansion_mode: str | None = Field(
        default="balanced",
        description=(
            "How much effort to spend rewriting the prompt before generation. "
            "'disabled' skips prompt expansion. 'fast' returns in about a second. "
            "'balanced' picks per request. 'quality' spends up to ~30s on a richer prompt."
        ),
    )
    target_audio_url: Annotated[str, Field(min_length=1, pattern=r"\S")] | None = Field(
        default=None,
        description=(
            "Optional URL of an audio clip at least 2 seconds long (maximum 15 MB) "
            "to pin to the generated soundtrack. Longer clips are trimmed to the "
            "generated video's length, keeping the beginning. The original audio "
            "replaces the output soundtrack, padded with silence if shorter than "
            "the video, without changing playback speed. Exceptionally high sample "
            "rates may be resampled to 96 kHz. Accepts an HTTP(S) URL or a base64 data URI."
        ),
    )


class MinimaxH3ReferenceBaseConfig(MinimaxH3BaseConfig):
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
    aspect_ratio: Literal["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
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
            "on. Reference images, videos, and audio clips must add up to at most 12 files."
        ),
    )
    reference_audio_urls: list[str] = Field(
        default_factory=list,
        max_length=3,
        description=(
            "URLs of reference audio clips (2-15 seconds each, combined duration at "
            "most 15 seconds), referenced in the prompt as Audio 1, Audio 2, and so on. "
            "Images, videos, and audio can be provided individually or together. "
            "Reference images, videos, and audio clips must add up to at most 12 files."
        ),
    )
    target_audio_url: Annotated[str, Field(min_length=1, pattern=r"\S")] | None = Field(
        default=None,
        description=(
            "Optional URL of an audio clip at least 2 seconds long (maximum 15 MB) "
            "to pin to the generated soundtrack. Cannot be combined with reference "
            "audio. Longer clips are trimmed to the generated video's length, keeping "
            "the beginning; shorter clips are padded with silence. The clip is "
            "resampled to 32 kHz stereo and replaces the output soundtrack without "
            "changing playback speed. Accepts an HTTP(S) URL or a base64 data URI."
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
        if self.target_audio_url is not None and self.reference_audio_urls:
            raise ValueError("target_audio_url cannot be combined with reference_audio_urls")
        return self

from __future__ import annotations

from typing import Annotated, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class MinimaxH3MaxTurboTextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max-turbo/text-to-video"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50_000,
        description="Text prompt for video generation",
    )
    duration: float = Field(
        default=5,
        ge=0.92,
        le=15,
        description=(
            "Video length in seconds. The output can run up to about 0.7 s longer "
            "than requested. Use at least 2 s with target_audio_url."
        ),
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
            "'disabled' skips prompt expansion. 'balanced' returns in about a second. "
            "'quality' spends up to ~30s on a richer prompt."
        ),
        json_schema_extra={"default": "balanced"},
    )
    aspect_ratio: Literal["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="16:9",
        description="The aspect ratio of the generated video.",
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

    @model_validator(mode="after")
    def validate_target_audio_duration(self) -> Self:
        if self.target_audio_url is not None and self.duration < 2:
            raise ValueError("duration must be >= 2 with target_audio_url")
        return self

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.minimax_h3_common import MinimaxH3ReferenceBaseConfig


class H3MaxTurboReferenceCondition(BaseFalConfig):
    """One ordered reference media condition."""

    type: Literal["image", "video", "audio"] = Field(
        ...,
        description="Reference modality. Cross-modality list order is semantic.",
    )
    url: str = Field(
        ...,
        min_length=1,
        description="URL of the reference media.",
    )


class MinimaxH3MaxTurboReferenceToVideoConfig(MinimaxH3ReferenceBaseConfig):
    app_id: Literal["minimax/h3-max-turbo/reference-to-video"]
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
    prompt_expansion_mode: str = Field(
        ...,
        description=(
            "How much effort to spend rewriting the prompt before generation. "
            "'disabled' skips prompt expansion. 'balanced' returns in about a second. "
            "'quality' spends up to ~30s on a richer prompt."
        ),
        json_schema_extra={"default": "balanced"},
    )
    reference_conditions: list[H3MaxTurboReferenceCondition] = Field(
        default_factory=list,
        max_length=12,
        description=(
            "Ordered reference list; cross-modality order is semantic and is "
            "preserved end-to-end. Do not combine with reference_*_urls."
        ),
    )

    @model_validator(mode="after")
    def validate_ordered_reference_constraints(self) -> Self:
        if self.reference_conditions and (
            self.reference_image_urls or self.reference_video_urls or self.reference_audio_urls
        ):
            raise ValueError("reference_conditions cannot be combined with reference_*_urls")
        if self.target_audio_url is not None:
            if any(reference.type == "audio" for reference in self.reference_conditions):
                raise ValueError(
                    "target_audio_url cannot be combined with audio reference_conditions"
                )
            if self.duration < 2:
                raise ValueError("duration must be >= 2 with target_audio_url")
        return self

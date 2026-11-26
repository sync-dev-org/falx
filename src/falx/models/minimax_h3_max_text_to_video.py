from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MinimaxH3MaxTextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max/text-to-video"]
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
    aspect_ratio: Literal["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="16:9",
        description="The aspect ratio of the generated video.",
    )

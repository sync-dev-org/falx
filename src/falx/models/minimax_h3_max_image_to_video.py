from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MinimaxH3MaxImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max/image-to-video"]
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
    image_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of the image to use as the first frame. When provided, the "
            "output aspect ratio follows this image. When omitted, the request is handled "
            "as text-to-video (16:9 by default)."
        ),
    )
    end_image_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of the image to use as the last frame, for first-to-last "
            "keyframe generation."
        ),
    )

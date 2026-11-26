from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Wan30PrimeImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["alibaba/wan-3.0-prime/image-to-video"]
    prompt: str | None = Field(
        default=None,
        max_length=5000,
        description="Text prompt describing the motion to generate.",
    )
    resolution: Literal["480p", "720p", "1080p"] = Field(
        default="1080p",
        description="Output video resolution tier.",
    )
    aspect_ratio: Literal["adaptive", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="adaptive",
        description="Output aspect ratio, or adaptive selection.",
    )
    duration: int | None = Field(
        default=5,
        ge=2,
        le=30,
        description=(
            "Output duration in seconds. Set to null for smart duration, which lets "
            "the model pick a length from the prompt and reference media."
        ),
    )
    audio: bool = Field(
        default=True,
        description="Include generated audio.",
    )
    enable_prompt_expansion: bool = Field(
        default=True,
        description=(
            "Enable intelligent prompt rewriting. Disabling it can save roughly "
            "20-60 seconds of latency but is likely to degrade generation quality."
        ),
    )
    enable_thinking: bool = Field(
        default=False,
        description="Enable enhanced reasoning before generation.",
    )
    seed: int | None = Field(
        default=None,
        ge=0,
        le=2_147_483_647,
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Enable content moderation for input and output. Disabling it requires "
            "account authorization; unauthorized requests are always checked."
        ),
    )
    start_image_url: str = Field(
        ...,
        description="First frame of the generated video.",
    )
    end_image_url: str | None = Field(
        default=None,
        description="Last frame of the generated video. Requires start_image_url.",
    )

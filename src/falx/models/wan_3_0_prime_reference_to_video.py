from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Wan30PrimeReferenceToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["alibaba/wan-3.0-prime/reference-to-video"]
    prompt: str | None = Field(
        default=None,
        max_length=5000,
        description=(
            "Text prompt directing how the reference media is used. Reference media "
            "can be addressed positionally, e.g. 'the subject in Image 1 walks past Video 1'."
        ),
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
    reference_image_urls: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Up to 10 reference image URLs.",
    )
    reference_video_urls: list[str] = Field(
        default_factory=list,
        max_length=5,
        description=(
            "Up to 5 reference video URLs totaling at most 15 seconds. "
            "Each clip must be at least 16 fps."
        ),
    )
    reference_audio_urls: list[str] = Field(
        default_factory=list,
        max_length=5,
        description="Up to 5 reference audio URLs totaling at most 15 seconds.",
    )
    file_url: str | None = Field(
        default=None,
        description="Document URL to base the video on. Requires enable_thinking=true.",
    )
    web_url: str | None = Field(
        default=None,
        description=(
            "Public webpage URL to base the video on. Requires enable_thinking=true. "
            "Only pages that do not require login can be read."
        ),
    )

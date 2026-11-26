from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.wan_3_0_prime_reference_to_video import Wan30PrimeReferenceToVideoConfig


class Wan30ReferenceToVideoConfig(Wan30PrimeReferenceToVideoConfig):
    app_id: Literal["alibaba/wan-3.0/reference-to-video"]
    prompt: str | None = Field(
        default=None,
        max_length=20_000,
        description=(
            "Text prompt directing how the reference media is used. Reference media "
            "can be addressed positionally, e.g. 'the subject in Image 1 walks past Video 1'."
        ),
    )
    reference_video_urls: list[str] = Field(
        default_factory=list,
        max_length=5,
        description=(
            "Up to 5 reference video URLs totaling at most 15 seconds. "
            "Each clip must be at least 16 fps. "
            "Input video duration is billed in addition to output duration."
        ),
    )

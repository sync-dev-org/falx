from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.wan_3_0_prime_text_to_video import Wan30PrimeTextToVideoConfig


class Wan30TextToVideoConfig(Wan30PrimeTextToVideoConfig):
    app_id: Literal["alibaba/wan-3.0/text-to-video"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=20_000,
        description="Text prompt for the generated video.",
    )

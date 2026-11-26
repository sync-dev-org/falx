from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.wan_3_0_prime_image_to_video import Wan30PrimeImageToVideoConfig


class Wan30ImageToVideoConfig(Wan30PrimeImageToVideoConfig):
    app_id: Literal["alibaba/wan-3.0/image-to-video"]
    prompt: str | None = Field(
        default=None,
        max_length=20_000,
        description="Text prompt describing the motion to generate.",
    )

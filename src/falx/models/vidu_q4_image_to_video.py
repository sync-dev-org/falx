from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.vidu_q4_common import ViduQ4BaseConfig


class ViduQ4ImageToVideoConfig(ViduQ4BaseConfig):
    app_id: Literal["fal-ai/vidu/q4/image-to-video"]
    prompt: str = Field(
        default="",
        max_length=5000,
        description="Text prompt for video generation, max 5000 characters",
    )
    image_url: str = Field(
        ...,
        description=(
            "URL or base64 data URI of the image to use as the first frame. "
            "Supports png, jpeg, jpg and webp up to 50 MB."
        ),
    )

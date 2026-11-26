from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.vidu_q3_image_to_video import ViduQ3ImageToVideoConfig


class ViduQ3ImageToVideoTurboConfig(ViduQ3ImageToVideoConfig):
    app_id: Literal["fal-ai/vidu/q3/image-to-video/turbo"]
    enable_safety_checker: bool | None = Field(
        default=True,
        description="Enable safety checks; disabling requires authorization.",
    )

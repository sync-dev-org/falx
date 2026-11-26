from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.vidu_q3_text_to_video import ViduQ3TextToVideoConfig


class ViduQ3TextToVideoTurboConfig(ViduQ3TextToVideoConfig):
    app_id: Literal["fal-ai/vidu/q3/text-to-video/turbo"]
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

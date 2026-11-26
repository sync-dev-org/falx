from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class GeminiOmniFlashV12UpscaleConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/v1.2/upscale"]
    video_url: str = Field(
        ...,
        description="URL of the video to upscale. Must be at most 15 seconds long.",
    )
    resolution: Literal["720p", "1080p", "4k"] = Field(
        default="1080p",
        description=(
            "The target resolution of the upscaled video. Must be higher than the source "
            "video's resolution."
        ),
    )

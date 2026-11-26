from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.gemini_omni_flash_v1_2_common import (
    GeminiOmniFlashV12Resolution,
)


class GeminiOmniFlashV12ExtendConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/v1.2/extend"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description="The text prompt describing how the video should continue.",
    )
    video_url: str = Field(
        ...,
        description=(
            "URL of the video to extend. Any length is accepted; the model conditions on the "
            "last 10 seconds and appends the continuation."
        ),
    )
    resolution: GeminiOmniFlashV12Resolution = Field(
        default="720p",
        description="The resolution of the extended video.",
    )
    duration: int = Field(
        default=8,
        ge=3,
        le=10,
        description="The duration of the continuation, in seconds.",
    )

from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.gemini_omni_flash_v1_1_common import GeminiOmniFlashV11Resolution


class GeminiOmniFlashV11EditConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/v1.1/edit"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description="A simple instruction describing the edit.",
    )
    video_url: str = Field(..., description="URL of the video to edit.")
    resolution: GeminiOmniFlashV11Resolution = Field(
        default="720p",
        description="The resolution of the edited video.",
    )

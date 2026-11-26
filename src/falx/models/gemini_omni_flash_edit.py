from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class GeminiOmniFlashEditConfig(BaseFalConfig):
    app_id: Literal["google/gemini-omni-flash/edit"]
    prompt: str = Field(
        ...,
        max_length=20_000,
        description=(
            'A simple instruction describing the edit. Simple prompts work best; add "Keep '
            'everything else the same." to preserve the rest of the scene. Voice editing is '
            "not supported."
        ),
    )
    video_url: str = Field(
        ...,
        description=(
            "URL of the video to edit. Note: editing uploaded videos is not available for "
            "users in the European Economic Area (EEA), Switzerland, and the United Kingdom."
        ),
    )

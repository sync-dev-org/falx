from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.veo3_1_common import VEO31_RESOLUTION_DESCRIPTION
from falx.models.veo3_1_text_to_video import Veo31TextToVideoConfig


class Veo31LiteTextToVideoConfig(Veo31TextToVideoConfig):
    app_id: Literal["fal-ai/veo3.1/lite"]
    resolution: Literal["720p", "1080p"] = Field(
        default="720p",
        description=VEO31_RESOLUTION_DESCRIPTION,
    )

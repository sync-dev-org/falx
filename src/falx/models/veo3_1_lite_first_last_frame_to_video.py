from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.veo3_1_common import VEO31_RESOLUTION_DESCRIPTION
from falx.models.veo3_1_first_last_frame_to_video import Veo31FirstLastFrameToVideoConfig


class Veo31LiteFirstLastFrameToVideoConfig(Veo31FirstLastFrameToVideoConfig):
    app_id: Literal["fal-ai/veo3.1/lite/first-last-frame-to-video"]
    resolution: Literal["720p", "1080p"] = Field(
        default="720p",
        description=VEO31_RESOLUTION_DESCRIPTION,
    )

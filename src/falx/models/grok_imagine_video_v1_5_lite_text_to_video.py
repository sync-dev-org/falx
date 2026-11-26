from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.grok_imagine_video_v1_5_lite_common import GrokImagineVideoV15LiteBaseConfig


class GrokImagineVideoV15LiteTextToVideoConfig(GrokImagineVideoV15LiteBaseConfig):
    app_id: Literal["xai/grok-imagine-video/v1.5/lite/text-to-video"]
    aspect_ratio: Literal["16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "21:9", "5:2"] = Field(
        default="16:9",
        description="Aspect ratio of the generated video.",
    )

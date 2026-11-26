from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.kling_v3_common import KlingV3AspectRatio
from falx.models.kling_v3_turbo_common import KlingV3TurboConfig


class KlingVideoV3TurboTextToVideoConfig(KlingV3TurboConfig):
    app_id: Literal[
        "fal-ai/kling-video/v3/turbo/standard/text-to-video",
        "fal-ai/kling-video/v3/turbo/pro/text-to-video",
    ]
    aspect_ratio: KlingV3AspectRatio = Field(
        default="16:9",
        description="The aspect ratio (width:height) of the generated video.",
    )

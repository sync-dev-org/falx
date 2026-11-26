from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.pixverse_v6_max_common import PixverseV6MaxBaseConfig


class PixverseV6MaxTextToVideoConfig(PixverseV6MaxBaseConfig):
    app_id: Literal["pixverse/v6/max/text-to-video", "fal-ai/pixverse/v6/text-to-video"]
    aspect_ratio: Literal["16:9", "4:3", "1:1", "3:4", "9:16", "2:3", "3:2", "21:9"] = Field(
        default="16:9",
        description="The aspect ratio of the generated video",
    )

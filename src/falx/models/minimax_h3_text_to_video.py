from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.minimax_h3_common import MinimaxH3BaseConfig


class MinimaxH3TextToVideoConfig(MinimaxH3BaseConfig):
    app_id: Literal["minimax/h3/text-to-video"]
    aspect_ratio: Literal["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="16:9",
        description="The aspect ratio of the generated video.",
    )

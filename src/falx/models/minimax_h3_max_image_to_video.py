from __future__ import annotations

from typing import Literal

from falx.models.minimax_h3_max_turbo_image_to_video import (
    MinimaxH3MaxTurboImageToVideoConfig,
)


class MinimaxH3MaxImageToVideoConfig(MinimaxH3MaxTurboImageToVideoConfig):
    app_id: Literal["minimax/h3-max/image-to-video"]

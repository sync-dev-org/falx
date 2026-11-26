from __future__ import annotations

from typing import Literal

from falx.models.minimax_h3_max_turbo_text_to_video import (
    MinimaxH3MaxTurboTextToVideoConfig,
)


class MinimaxH3MaxTextToVideoConfig(MinimaxH3MaxTurboTextToVideoConfig):
    app_id: Literal["minimax/h3-max/text-to-video"]

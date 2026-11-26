from __future__ import annotations

from typing import Literal

from falx.models.minimax_h3_common import MinimaxH3ReferenceBaseConfig


class MinimaxH3ReferenceToVideoConfig(MinimaxH3ReferenceBaseConfig):
    app_id: Literal["minimax/h3/reference-to-video"]

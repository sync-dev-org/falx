from __future__ import annotations

from typing import Literal

from falx.models.lyria3 import Lyria3Config


class Lyria3ProConfig(Lyria3Config):
    app_id: Literal["fal-ai/lyria3/pro"]

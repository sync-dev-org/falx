from __future__ import annotations

from typing import Literal

from falx.models.veo3_common import Veo3Common


class Veo3TextToVideoConfig(Veo3Common):
    app_id: Literal["fal-ai/veo3", "fal-ai/veo3/fast"]

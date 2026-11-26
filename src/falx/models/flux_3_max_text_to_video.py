from __future__ import annotations

from typing import Literal

from falx.models.flux_3_max_common import Flux3MaxBaseConfig


class Flux3MaxTextToVideoConfig(Flux3MaxBaseConfig):
    app_id: Literal["blackforestlabs/flux-3-max/text-to-video"]

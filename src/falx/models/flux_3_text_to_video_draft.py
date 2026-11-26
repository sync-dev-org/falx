from __future__ import annotations

from typing import Literal

from falx.models.flux_3_draft_common import Flux3DraftBaseConfig


class Flux3TextToVideoDraftConfig(Flux3DraftBaseConfig):
    app_id: Literal["blackforestlabs/flux-3/text-to-video/draft"]

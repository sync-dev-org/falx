from __future__ import annotations

from typing import Literal

from falx.models.vidu_q3_reference_to_video import ViduQ3ReferenceToVideoBase


class ViduQ3ReferenceToVideoMixConfig(ViduQ3ReferenceToVideoBase):
    app_id: Literal["fal-ai/vidu/q3/reference-to-video/mix"]

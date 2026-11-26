from __future__ import annotations

from typing import ClassVar, Literal

from falx.models.kling_v3_pro_text_to_video import KlingVideoV3ProTextToVideoConfig


class KlingVideoV34kTextToVideoConfig(KlingVideoV3ProTextToVideoConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/v3/4k/text-to-video"]

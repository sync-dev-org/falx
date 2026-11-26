from __future__ import annotations

from typing import ClassVar, Literal

from falx.models.kling_o3_pro_text_to_video import KlingVideoO3ProTextToVideoConfig


class KlingVideoO34kTextToVideoConfig(KlingVideoO3ProTextToVideoConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/4k/text-to-video"]

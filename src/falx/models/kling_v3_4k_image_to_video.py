from __future__ import annotations

from typing import ClassVar, Literal

from falx.models.kling_v3_pro_image_to_video import KlingVideoV3ProImageToVideoConfig


class KlingVideoV34kImageToVideoConfig(KlingVideoV3ProImageToVideoConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/v3/4k/image-to-video"]

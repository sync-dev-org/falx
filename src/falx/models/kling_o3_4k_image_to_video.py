from __future__ import annotations

from typing import ClassVar, Literal

from falx.models.kling_o3_pro_image_to_video import KlingVideoO3ProImageToVideoConfig


class KlingVideoO34kImageToVideoConfig(KlingVideoO3ProImageToVideoConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/4k/image-to-video"]

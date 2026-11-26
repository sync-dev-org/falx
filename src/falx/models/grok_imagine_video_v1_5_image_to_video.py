from __future__ import annotations

from typing import Literal

from falx.models.grok_imagine_video_v1_5_lite_image_to_video import (
    GrokImagineVideoV15LiteImageToVideoConfig,
)


class GrokImagineVideoV15ImageToVideoConfig(GrokImagineVideoV15LiteImageToVideoConfig):
    app_id: Literal["xai/grok-imagine-video/v1.5/image-to-video"]

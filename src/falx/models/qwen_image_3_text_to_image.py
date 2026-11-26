from __future__ import annotations

from typing import Literal

from falx.models.qwen_image_3_common import QwenImage3Common


class QwenImage3TextToImageConfig(QwenImage3Common):
    app_id: Literal["alibaba/qwen-image-3/text-to-image"]

from __future__ import annotations

from typing import Literal

from falx.models.kling_v4_image_common import KlingV4ImageCommon


class KlingV4TextToImageConfig(KlingV4ImageCommon):
    app_id: Literal["kling/v4/text-to-image"]

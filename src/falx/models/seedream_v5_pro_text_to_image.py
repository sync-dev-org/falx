from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v5_pro_common import SeedreamV5ProCommon


class SeedreamV5ProTextToImageConfig(SeedreamV5ProCommon):
    app_id: Literal["bytedance/seedream/v5/pro/text-to-image"]
    prompt: str = Field(
        ...,
        description="The text prompt used to generate the image.",
    )

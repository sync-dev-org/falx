from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v5_flash_common import SeedreamV5FlashCommon


class SeedreamV5FlashTextToImageConfig(SeedreamV5FlashCommon):
    app_id: Literal["bytedance/seedream/v5/flash/text-to-image"]
    prompt: str = Field(
        ...,
        description="The text prompt used to generate the image.",
    )

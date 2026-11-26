from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedance25_flash_common import Seedance25FlashCommon


class Seedance25FlashTextToVideoConfig(Seedance25FlashCommon):
    app_id: Literal["bytedance/seedance-2.5/flash/text-to-video"]
    prompt: str = Field(
        ...,
        description="The text prompt used to generate the video",
    )

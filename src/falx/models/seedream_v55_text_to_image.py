from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v55_common import SeedreamV55Common


class SeedreamV55TextToImageConfig(SeedreamV55Common):
    app_id: Literal["bytedance/seedream/v5.5/text-to-image"]
    prompt: str = Field(
        ...,
        description="The text prompt used to generate the image.",
    )

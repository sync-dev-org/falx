from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v55_common import SeedreamV55Common


class SeedreamV55EditConfig(SeedreamV55Common):
    app_id: Literal["bytedance/seedream/v5.5/edit"]
    prompt: str = Field(
        ...,
        description="The text prompt used to edit the image.",
    )
    image_urls: list[str] = Field(
        ...,
        description=(
            "List of URLs of input reference images. Up to 10 images are supported; "
            "if more are sent, only the last 10 are used."
        ),
    )

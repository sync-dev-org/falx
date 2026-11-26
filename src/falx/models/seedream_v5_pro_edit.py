from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v5_pro_common import SeedreamV5ProGenerationCommon


class SeedreamV5ProEditConfig(SeedreamV5ProGenerationCommon):
    app_id: Literal["bytedance/seedream/v5/pro/edit"]
    prompt: str = Field(
        ...,
        description="The text prompt used to edit the image.",
    )
    background: Literal["opaque", "transparent"] = Field(
        default="opaque",
        description=(
            "Use `transparent` with exactly one alpha-channel reference and PNG output "
            "to preserve transparency."
        ),
    )
    image_urls: list[str] = Field(
        ...,
        description=(
            "List of URLs of input reference images. Up to 10 images are supported; "
            "if more are sent, only the last 10 are used."
        ),
    )

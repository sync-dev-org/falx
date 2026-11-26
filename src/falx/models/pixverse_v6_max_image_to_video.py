from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.pixverse_v6_max_common import PixverseV6MaxBaseConfig


class PixverseV6MaxImageToVideoConfig(PixverseV6MaxBaseConfig):
    app_id: Literal["pixverse/v6/max/image-to-video", "fal-ai/pixverse/v6/image-to-video"]
    image_url: str = Field(
        ...,
        description="URL of the image to use as the first frame",
    )

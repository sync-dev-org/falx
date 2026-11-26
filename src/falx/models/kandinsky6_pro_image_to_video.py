from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.kandinsky6_pro_common import Kandinsky6ProBaseConfig


class Kandinsky6ProImageToVideoConfig(Kandinsky6ProBaseConfig):
    app_id: Literal["fal-ai/kandinsky6-pro/image-to-video"]
    image_url: str = Field(
        ...,
        description="The image used as the first frame of the video.",
    )
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4", "auto"] = Field(
        default="auto",
        description=(
            "The aspect ratio of the generated video. `auto` picks the supported ratio "
            "closest to the image's; the image is center-cropped to it."
        ),
    )

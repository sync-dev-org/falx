from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.kandinsky6_pro_common import Kandinsky6ProBaseConfig


class Kandinsky6ProTextToVideoConfig(Kandinsky6ProBaseConfig):
    app_id: Literal["fal-ai/kandinsky6-pro/text-to-video"]
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4"] = Field(
        default="16:9",
        description="The aspect ratio of the generated video.",
    )

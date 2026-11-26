from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.pixverse_v6_max_common import PixverseV6MaxBaseConfig


class PixverseV6TransitionConfig(PixverseV6MaxBaseConfig):
    app_id: Literal["fal-ai/pixverse/v6/transition"]
    prompt: str = Field(
        ...,
        description=(
            "The prompt for the transition. Limited to 2048 UTF-8 encoded bytes. "
            "Because the limit counts bytes rather than characters, emoji and non-Latin "
            "or accented characters (which use multiple bytes each) can push a visually "
            "short prompt over the cap."
        ),
    )
    first_image_url: str = Field(
        ...,
        description="URL of the image to use as the first frame",
    )
    end_image_url: str = Field(
        ...,
        description="URL of the image to use as the last frame",
    )
    aspect_ratio: Literal["16:9", "4:3", "1:1", "3:4", "9:16", "2:3", "3:2", "21:9"] = Field(
        default="16:9",
        description="The aspect ratio of the generated video",
    )

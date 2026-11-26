from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.minimax_h3_common import MinimaxH3BaseConfig


class MinimaxH3ImageToVideoConfig(MinimaxH3BaseConfig):
    app_id: Literal["minimax/h3/image-to-video"]
    image_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of the image to use as the first frame. When provided, the "
            "output canvas follows this image. If only end_image_url is provided, the "
            "canvas follows that last frame instead. If both images are omitted, the "
            "request is handled as text-to-video (16:9 by default)."
        ),
    )
    end_image_url: str | None = Field(
        default=None,
        description=(
            "Optional URL of the image to use as the last frame. It may be provided "
            "alone for end-only keyframe generation; in that case the output canvas "
            "follows this image."
        ),
    )

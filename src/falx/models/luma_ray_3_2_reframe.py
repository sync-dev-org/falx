from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.luma_ray_3_2_common import (
    LUMA_RAY_32_ASPECT_RATIO_DESCRIPTION,
    LUMA_RAY_32_RESOLUTION_DESCRIPTION,
    LumaRay32AspectRatio,
    LumaRay32ReframeSourcePosition,
    LumaRay32Resolution,
)


class LumaRay32ReframeConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["luma/agent/ray/v3.2/reframe"]
    prompt: str = Field(
        ...,
        description=(
            "Text prompt describing the content to paint into the newly exposed "
            "canvas area when reframing to the target aspect ratio."
        ),
    )
    video_url: str = Field(
        ...,
        description="URL of the source video to reframe (must be 30 seconds or less).",
    )
    aspect_ratio: LumaRay32AspectRatio = Field(
        ...,
        description=LUMA_RAY_32_ASPECT_RATIO_DESCRIPTION,
    )
    resolution: LumaRay32Resolution = Field(
        default="540p",
        description=LUMA_RAY_32_RESOLUTION_DESCRIPTION,
    )
    source_position: LumaRay32ReframeSourcePosition | None = Field(
        default=None,
        description=(
            "Optional normalized source rectangle controlling where the source video "
            "sits in the output canvas."
        ),
    )

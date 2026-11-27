from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class RecraftVectorizeProConfig(BaseFalConfig):
    app_id: Literal["recraft/vectorize/pro"]
    image_url: str = Field(
        ...,
        description=(
            "The URL of the image to be vectorized. Must be in PNG, JPG or WEBP format, "
            "less than 5 MB in size, have resolution less than 16 MP and max dimension "
            "less than 4096 pixels, min dimension more than 256 pixels."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )
    shape_stacking: Literal["hierarchical", "cut_out"] = Field(
        default="hierarchical",
        description=(
            "How shapes are layered in the SVG. `hierarchical` stacks shapes so lower "
            "shapes stay whole and are partly covered by the ones above. `cut_out` "
            "makes shapes not overlap, so each visible region belongs to one shape, "
            "which suits plotters, vinyl cutters and screen printing."
        ),
    )

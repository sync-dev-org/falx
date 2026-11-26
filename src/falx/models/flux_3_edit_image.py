from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_image_common import Flux3ImageBaseConfig
from falx.models.flux_3_klein_common import Flux3KleinEditBoundingBox


class Flux3EditImageConfig(Flux3ImageBaseConfig):
    app_id: Literal["blackforestlabs/flux-3/edit-image"]
    bounding_boxes: list[Flux3KleinEditBoundingBox] | None = Field(
        default=None,
        max_length=32,
        description=(
            "Optional layout, with (0, 0) at the top-left of each image: keep, move, resize or "
            "remove objects from the references, or place new ones. Name boxes in the prompt "
            "by label, e.g. `<dragon>`."
        ),
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description=(
            "Reference image URLs or data URIs, in image 1 through image 10 order. "
            "Each must be at least 256 pixels per dimension. Oversized images are "
            "automatically downscaled to at most 4 megapixels while preserving aspect ratio. "
            "The first controls auto aspect ratio."
        ),
    )

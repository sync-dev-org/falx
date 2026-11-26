from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_image_common import Flux3ImageBaseConfig
from falx.models.flux_3_klein_common import Flux3KleinBoundingBox


class Flux3TextToImageConfig(Flux3ImageBaseConfig):
    app_id: Literal["blackforestlabs/flux-3/text-to-image"]
    bounding_boxes: list[Flux3KleinBoundingBox] | None = Field(
        default=None,
        max_length=32,
        description=(
            "Optional layout: draw each described object inside its box. Box edges are "
            "fractions of the image size, with (0, 0) at the top-left. Name boxes in the prompt "
            "by label, e.g. `A red fox <fox> sits under a red umbrella <umbrella>`."
        ),
    )

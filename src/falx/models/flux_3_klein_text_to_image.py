from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_klein_common import (
    FLUX3_KLEIN_IMAGE_SIZE_LIMITS,
    Flux3KleinBaseLoraConfig,
    Flux3KleinBoundingBox,
    Flux3KleinCommon,
    Flux3KleinImageSize,
    Flux3KleinImageSizePreset,
    Flux3KleinLoraConfig,
)


class Flux3KleinTextToImageConfig(Flux3KleinCommon):
    app_id: Literal["blackforestlabs/flux-3/klein/text-to-image"]
    image_size: Flux3KleinImageSize | Flux3KleinImageSizePreset = Field(
        default="square_hd",
        description=(
            "The size of the generated image. Each side can be 256 to 4096 pixels (native 4K)."
        ),
        json_schema_extra={"x-fal": FLUX3_KLEIN_IMAGE_SIZE_LIMITS},
    )
    bounding_boxes: list[Flux3KleinBoundingBox] | None = Field(
        default=None,
        max_length=32,
        description=(
            "Optional layout: draw each described object inside its box. Box edges are "
            "fractions of the image size, with (0, 0) at the top-left. Name boxes in the prompt "
            "by label, e.g. `A red fox <fox> sits under a red umbrella <umbrella>`."
        ),
    )


class Flux3KleinTextToImageLoraConfig(Flux3KleinTextToImageConfig, Flux3KleinLoraConfig):
    app_id: Literal["blackforestlabs/flux-3/klein/text-to-image/lora"]


class Flux3KleinBaseTextToImageLoraConfig(Flux3KleinTextToImageConfig, Flux3KleinBaseLoraConfig):
    app_id: Literal["blackforestlabs/flux-3/klein/base/text-to-image/lora"]

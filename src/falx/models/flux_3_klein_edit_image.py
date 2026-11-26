from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.flux_3_klein_common import (
    FLUX3_KLEIN_IMAGE_SIZE_LIMITS,
    Flux3KleinBaseLoraConfig,
    Flux3KleinCommon,
    Flux3KleinEditBoundingBox,
    Flux3KleinImageSize,
    Flux3KleinImageSizePreset,
    Flux3KleinLoraConfig,
)


class Flux3KleinEditImageConfig(Flux3KleinCommon):
    app_id: Literal["blackforestlabs/flux-3/klein/edit-image"]
    prompt: str = Field(
        ...,
        description=(
            "A complete caption of the target image with the edit folded in. Refer to the "
            "references by their order: the first image, the second image."
        ),
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="The reference images to edit or compose from (up to 10).",
    )
    image_size: Flux3KleinImageSize | Flux3KleinImageSizePreset | None = Field(
        default=None,
        description=(
            "The size of the generated image, 256 to 4096 pixels per side. If not set, a single "
            "reference image's own size (scaled to at most 4 megapixels) is used, or the first "
            "reference image's size (at most 1 megapixel) when several are given."
        ),
        json_schema_extra={"x-fal": FLUX3_KLEIN_IMAGE_SIZE_LIMITS},
    )
    bounding_boxes: list[Flux3KleinEditBoundingBox] | None = Field(
        default=None,
        max_length=32,
        description=(
            "Optional layout, with (0, 0) at the top-left of each image: keep, move, resize or "
            "remove objects from the references, or place new ones. Name boxes in the prompt "
            "by label, e.g. `<dragon>`."
        ),
    )


class Flux3KleinEditImageLoraConfig(Flux3KleinEditImageConfig, Flux3KleinLoraConfig):
    app_id: Literal["blackforestlabs/flux-3/klein/edit-image/lora"]


class Flux3KleinBaseEditImageLoraConfig(Flux3KleinEditImageConfig, Flux3KleinBaseLoraConfig):
    app_id: Literal["blackforestlabs/flux-3/klein/base/edit-image/lora"]

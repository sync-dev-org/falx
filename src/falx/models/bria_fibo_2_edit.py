from __future__ import annotations

from typing import Literal, Self

from pydantic import AliasChoices, Field, model_validator

from falx.models.bria_fibo_2_common import (
    BriaFibo2AspectRatio,
    BriaFibo2BaseConfig,
    BriaFibo2VglEdit,
)


class BriaFibo2EditConfig(BriaFibo2BaseConfig):
    app_id: Literal["bria/fibo-2/edit"]
    image_urls: list[str] = Field(
        ...,
        max_length=4,
        min_length=1,
        description=(
            "1-4 images to edit (files or URLs). The instruction refers to them as "
            "<image_1>, <image_2> and so on, in the order they are sent."
        ),
    )
    instruction: str | None = Field(
        default=None,
        validation_alias=AliasChoices("instruction", "prompt"),
        description=(
            "The edit, in free-form text. It is expanded into a VGL, which is "
            "returned. With 'vgl', the change to make to it. 'prompt' is accepted as "
            "an alias."
        ),
    )
    aspect_ratio: BriaFibo2AspectRatio | None = Field(
        default=None,
        description=(
            "Output aspect ratio, at about one megapixel. Left unset, the output keeps "
            "the ratio of the first image. A single image always keeps its own ratio."
        ),
    )
    mask_url: str | None = Field(
        default=None,
        description=(
            "Mask (file or URL) marking the region to regenerate: white where the "
            "model should edit, black elsewhere. Single-image requests only, at that "
            "image's size. A masked edit comes back at the image's own size, with its "
            "own pixels outside the mask."
        ),
    )
    vgl: BriaFibo2VglEdit | None = Field(
        default=None,
        description=(
            "A VGL (Visual Generation Language) document. Alone, it is the edit as-is "
            "and must carry its 'edit_instruction'. With 'instruction', it is the "
            "first image's VGL, the baseline the edit is written from. Accepts what a "
            "previous request returned."
        ),
    )

    @model_validator(mode="after")
    def validate_edit_inputs(self) -> Self:
        if self.mask_url is not None and len(self.image_urls) != 1:
            raise ValueError("mask_url is supported only with a single image")
        if self.vgl is not None and self.instruction is None and self.vgl.edit_instruction is None:
            raise ValueError("vgl requires edit_instruction when instruction is omitted")
        return self

from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class BriaFiboEdit15ExpandConfig(BaseFalConfig):
    """An expansion request: an image, a canvas to grow it into,
    and optionally what to put there.
    """

    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["bria/fibo-edit-1.5/expand"]
    image_url: str = Field(
        ...,
        description="The image to expand (file or URL).",
    )
    canvas_size: list[int] | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        description=(
            "The desired size of the final image after the expansion, as [width, "
            "height]. Area must be under 25 megapixels. Pairs with "
            "'original_image_location'."
        ),
    )
    aspect_ratio: (
        Literal["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9"] | None
    ) = Field(
        default=None,
        description=(
            "The desired aspect ratio of the final image. Used over "
            "'original_image_size' and 'original_image_location' if provided: the "
            "original is centred and the canvas grows around it."
        ),
    )
    original_image_size: list[int] | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        description=(
            "The desired size of the original inside the canvas, as [width, height]; "
            "it is resized to this before being placed. Ignored if 'aspect_ratio' is "
            "provided."
        ),
    )
    original_image_location: list[int] | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        description=(
            "Top-left corner of the original within the canvas, as [x, y]. May sit "
            "outside the canvas, in which case the original is cropped. Ignored if "
            "'aspect_ratio' is provided."
        ),
    )
    prompt: str | None = Field(
        default=None,
        description=(
            "What should appear in the expanded area. Omit it and the model is asked "
            "only to extend the image, which is usually what you want for a plain "
            "canvas change."
        ),
    )
    seed: int | None = Field(
        default=None,
        ge=0,
        le=2147483647,
        description=(
            "Reuse the seed from a previous response to recreate that result. Omit it "
            "for a random one, which is reported in the response either way."
        ),
    )
    negative_prompt: str | None = Field(
        default=None,
        description=(
            "Not supported by this model, and refused rather than ignored -- see "
            "'prompt'. Present only so a request written against the SDXL expansion "
            "endpoint fails loudly here instead of silently losing the field."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description="If true, returns the image directly in the response (increases latency).",
    )
    retain_original_quality: bool = Field(
        default=True,
        description=(
            "Keep the original's own pixels at full resolution. Generation happens "
            "near one megapixel, so a larger canvas is scaled up afterwards; leave "
            "this on and the region the mask protected is not resampled at all. Turn "
            "it off for a uniformly soft result, which can hide the seam on a textured "
            "background."
        ),
    )
    preserve_alpha: bool = Field(
        default=True,
        description=(
            "Keep the input's transparency. The model works in RGB, so the alpha "
            "channel is not generated -- the original's own is extended outwards by "
            "replicating its edges, which is what expanding a cutout means. Turn it "
            "off to get a flattened RGB result."
        ),
    )
    return_model_output: bool = Field(
        default=False,
        description=(
            "Also return the model's own frame, before the original was pasted back "
            "and the seam blended. Diagnostic only -- it does not change the returned "
            "image. Use it to tell a bad generation apart from a bad composite: a "
            "boundary already broken in that frame came from the model, not from "
            "post-processing."
        ),
    )

    @model_validator(mode="after")
    def validate_expansion_inputs(self) -> Self:
        if self.negative_prompt is not None:
            raise ValueError("negative_prompt is not supported")
        if self.aspect_ratio is None and (
            (self.canvas_size is None) != (self.original_image_location is None)
        ):
            raise ValueError("canvas_size and original_image_location must be provided together")
        return self

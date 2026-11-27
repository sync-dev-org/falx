from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.gpt_image_2 import ImageSize, ImageSizePreset


class GptImage26Common(BaseFalConfig):
    """Shared parameters for GPT Image 2.6 generation and edit endpoints."""

    random_seed_field: ClassVar[str | None] = None

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=32_000,
        description="The prompt for image generation",
    )
    image_size: ImageSizePreset | ImageSize = Field(
        default="landscape_4_3",
        description=(
            "The size of the generated image. Supports preset names, explicit {width, height}, "
            "or 'auto' to let the model pick the best size. Concrete sizes must have both "
            "dimensions as multiples of 16, max edge 3840px, aspect ratio <= 3:1, total pixels "
            "between 655,360 and 8,294,400."
        ),
    )
    quality: Literal["auto", "low", "medium", "high", "xhigh", "max"] = Field(
        default="high",
        description=(
            "Rendering quality for the generated image. For SVG output it controls the "
            "reference image used to create the vector."
        ),
    )
    reasoning_effort: Literal["low", "medium", "high"] = Field(
        default="high",
        description=(
            "How much the model plans before rendering, independently of quality "
            "(OpenAI `complexity`). Higher levels can help with dense text and complex "
            "layouts but add latency."
        ),
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=10,
        title="Number of Images",
        description=(
            "Number of images to generate. Must be 1 for SVG output. For GIF output, "
            "all frames of all outputs share the request's pixel budget."
        ),
    )
    background: Literal["auto", "transparent", "opaque"] = Field(
        default="auto",
        description="Background for the generated image",
    )
    output_compression: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description=(
            "Compression level from 0 to 100. Only supported when output_format is "
            "'jpeg' or 'webp'."
        ),
    )
    frame_count: int = Field(
        default=9,
        ge=2,
        le=16,
        description=(
            "GIF only: number of frames. image_size applies to each frame; reduce size "
            "or count if the request exceeds the pixel budget."
        ),
    )
    frame_duration_ms: int = Field(
        default=200,
        ge=20,
        le=2000,
        description="GIF only: milliseconds per frame, rounded to 10 ms.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If `True`, the media will be returned as a data URI and the output data "
            "won't be available in the request history."
        ),
    )


class GptImage26TextToImageCommon(GptImage26Common):
    """Shared text-to-image parameters, including SVG output options."""

    output_format: Literal["jpeg", "png", "webp", "gif", "svg"] = Field(
        default="png",
        description=(
            "Output format for the images. 'gif' returns an animation and 'svg' a vector image."
        ),
    )
    svg_model: Literal[
        "gpt-6-astra", "gpt-5.5", "gpt-5.4", "gpt-5.6-terra", "gpt-6-luna", "gpt-6-sol"
    ] = Field(
        default="gpt-6-astra",
        description=(
            "SVG only: the model that converts the generated reference image into vector "
            "paths. Larger models produce more accurate shapes."
        ),
    )

    @model_validator(mode="after")
    def validate_svg_image_count(self) -> GptImage26TextToImageCommon:
        if self.output_format == "svg" and self.num_images != 1:
            raise ValueError("num_images must be 1 for SVG output")
        return self


class GptImage26FlareTextToImageConfig(GptImage26TextToImageCommon):
    app_id: Literal["openai/gpt-image-2.6/flare/text-to-image"]


class GptImage26SunburstTextToImageConfig(GptImage26TextToImageCommon):
    app_id: Literal["openai/gpt-image-2.6/sunburst/text-to-image"]

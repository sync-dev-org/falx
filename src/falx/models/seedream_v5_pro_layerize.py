from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class SeedreamV5ProLayerizeConfig(BaseFalConfig):
    app_id: Literal["bytedance/seedream/v5/pro/layerize"]
    prompt: str = Field(
        default="",
        description=(
            "Optional instructions describing which elements to separate. When empty, "
            "the model automatically separates the major elements. Normalized "
            "<bbox>left top right bottom</bbox> tags may be used for precise coordinate "
            "targeting."
        ),
    )
    image_url: str = Field(
        ...,
        description=(
            "URL of the image to decompose into a base image and independently editable "
            "layers. The image must contain between 512x512 and 6000x6000 total pixels, "
            "have an aspect ratio between 1/16 and 16, and be no larger than 30 MB."
        ),
    )
    image_size: Literal["auto", "auto_1K", "auto_1.5K", "auto_2K"] = Field(
        default="auto",
        description=(
            "Resolution tier for the output base image and layers. auto adapts to the "
            "input image while preserving each element's aspect ratio."
        ),
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="png",
        description="Format of the base image. Separated layers always use PNG.",
    )
    watermark: bool = Field(
        default=False,
        description="Whether to add the provider's visible watermark.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "When true, generated media is returned as a data URI and is not available "
            "in request history."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "Enables the safety checker. Disabling it requires account authorization; "
            "unauthorized requests are always checked."
        ),
    )
    enhance_prompt_mode: Literal["standard", "fast"] = Field(
        default="standard",
        description=(
            "Prompt optimization mode. standard prioritizes image quality; fast reduces "
            "generation time."
        ),
    )

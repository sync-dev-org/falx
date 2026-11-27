from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v5_flash_layerize import SeedreamV5FlashLayerizeConfig


class SeedreamV55LayerizeConfig(SeedreamV5FlashLayerizeConfig):
    app_id: Literal["bytedance/seedream/v5.5/layerize"]
    prompt: str = Field(
        default="",
        description=(
            "Optional instructions describing which elements to separate. When empty, "
            "the model automatically separates the major elements. Normalized "
            "`<bbox>left top right bottom</bbox>` tags may be used for precise "
            "coordinate targeting."
        ),
    )
    image_size: Literal["auto", "auto_1K", "auto_1.5K", "auto_2K"] = Field(
        default="auto",
        description=(
            "Resolution tier for the output base image and layers. `auto` adapts to "
            "the input image while preserving each element's aspect ratio."
        ),
    )
    max_images: int = Field(
        default=30,
        ge=2,
        le=100,
        description=(
            "Maximum number of output images, including the base image. Higher values "
            "usually produce a finer decomposition. Above 30, images are always "
            "returned as URLs and `sync_mode` is ignored."
        ),
    )
    enable_text_recognition: bool = Field(
        default=False,
        description=(
            "If `True`, formatted text layers include a rich-text OCR result in `text_recognition`."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If `True`, the media will be returned as a data URI and the output data "
            "won't be available in the request history."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "If set to true, the safety checker will be enabled. Disabling it requires "
            "account authorization; unauthorized requests are always checked."
        ),
    )

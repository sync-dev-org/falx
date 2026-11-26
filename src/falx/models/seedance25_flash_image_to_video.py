from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedance25_flash_common import Seedance25FlashCommon


class Seedance25FlashImageToVideoConfig(Seedance25FlashCommon):
    app_id: Literal["bytedance/seedance-2.5/flash/image-to-video"]
    prompt: str | None = Field(
        default=None,
        description="The text prompt describing the desired motion and action for the video.",
    )
    image_url: str = Field(
        ...,
        description=(
            "The URL of the starting frame image to animate. Supported formats: JPEG, PNG, "
            "WebP, BMP, TIFF, GIF, HEIC, HEIF. Max 30 MB."
        ),
    )
    end_image_url: str | None = Field(
        default=None,
        description=(
            "The URL of the image to use as the last frame of the video. When provided, "
            "the generated video will transition from the starting image to this ending "
            "image. Supported formats: JPEG, PNG, WebP, BMP, TIFF, GIF, HEIC, HEIF. Max 30 MB."
        ),
    )
    aspect_ratio: Literal["auto"] = Field(
        default="auto",
        description='The aspect ratio of the generated video. Always "auto" for image-to-video',
    )

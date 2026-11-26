from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedance_us_common import SeedanceUsVideoConfig


class Seedance2UsImageToVideoConfig(SeedanceUsVideoConfig):
    app_id: Literal["bytedance/seedance-2.0/us/image-to-video"]
    prompt: str = Field(
        ...,
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
    aspect_ratio: Literal["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="auto",
        description=(
            "The aspect ratio of the generated video. Use 16:9 for landscape, 9:16 for "
            "portrait/vertical, 1:1 for square, 21:9 for ultrawide cinematic, or auto "
            "to infer from the input image."
        ),
    )

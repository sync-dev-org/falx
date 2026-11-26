from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.nano_banana_2 import NanoBanana2Common
from falx.models.nano_banana_common import NanoBananaExtendedAspectRatio


class NanoBanana2EditConfig(NanoBanana2Common):
    app_id: Literal["fal-ai/nano-banana-2/edit", "fal-ai/gemini-3.1-flash-image-preview/edit"]
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=50000,
        description="The prompt for image editing.",
    )
    image_urls: list[str] = Field(
        default_factory=list,
        description=(
            "The URLs of the images to use for image-to-image generation or image editing. "
            "Optional when at least one of `video_url`, `audio_url`, or `pdf_url` is provided."
        ),
    )
    aspect_ratio: NanoBananaExtendedAspectRatio | None = Field(
        default="auto",
        description=(
            "The aspect ratio of the generated image. Supports extreme ratios: 4:1, 1:4, 8:1, 1:8."
        ),
    )
    video_url: str | None = Field(
        default=None,
        description=(
            "Optional video to use as input context. Accepts an http(s)/data URL to a video "
            "file (downloaded and sent inline, max 15MB) or a YouTube URL (passed through to "
            "the model without downloading)."
        ),
    )
    audio_url: str | None = Field(
        default=None,
        description=(
            "Optional audio file to use as input context. Accepts an http(s)/data URL "
            "(downloaded and sent inline, max 15MB)."
        ),
    )
    pdf_url: str | None = Field(
        default=None,
        description=(
            "Optional PDF document to use as input context. Accepts an http(s)/data URL "
            "(downloaded and sent inline, max 15MB)."
        ),
    )

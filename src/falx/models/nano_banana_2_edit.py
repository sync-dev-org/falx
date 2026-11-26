from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models.nano_banana_2 import NanoBanana2Common


class NanoBanana2EditConfig(NanoBanana2Common):
    app_id: Literal["fal-ai/nano-banana-2/edit"]
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=50000,
        description="Prompt for image editing.",
    )
    image_urls: list[str] | None = Field(
        default=None,
        min_length=1,
        description=(
            "Image URLs to use for image-to-image generation or image editing. "
            "Optional when at least one of video_url, audio_url, or pdf_url is provided."
        ),
    )
    video_url: str | None = Field(
        default=None,
        description=(
            "Optional video to use as input context. Accepts an http(s)/data URL "
            "to a video file (downloaded and sent inline, max 15MB) or a YouTube URL "
            "(passed through to the model without downloading)."
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

    @model_validator(mode="after")
    def validate_input_context(self) -> Self:
        if (
            self.image_urls is None
            and self.video_url is None
            and self.audio_url is None
            and self.pdf_url is None
        ):
            raise ValueError("image_urls, video_url, audio_url, or pdf_url is required")
        return self

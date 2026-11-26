from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models.nano_banana_2_1 import NanoBanana21AspectRatio, NanoBanana21Common


class NanoBanana21EditConfig(NanoBanana21Common):
    schema_example_parameters: ClassVar[dict[str, Any]] = {
        "image_urls": ["https://example.com/input"],
    }

    app_id: Literal["google/nano-banana-2.1/edit"]
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=50000,
        description="The prompt for image editing.",
    )
    aspect_ratio: NanoBanana21AspectRatio | None = Field(
        default="auto",
        description=(
            "The aspect ratio of the generated image. Supports extreme ratios: 4:1, 1:4, 8:1, 1:8."
        ),
    )
    image_urls: list[str] = Field(
        default_factory=list,
        description=(
            "The URLs of the images to use for image-to-image generation or image editing. "
            "Optional when `video_url` or `pdf_url` is provided."
        ),
    )
    video_url: str | None = Field(
        default=None,
        description=(
            "Optional video to use as input context. Accepts an http(s)/data URL to a "
            "video file (downloaded and sent inline, max 15MB) or a YouTube URL "
            "(passed through to the model without downloading)."
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
        if not (self.image_urls or self.video_url or self.pdf_url):
            raise ValueError("image_urls, video_url, or pdf_url is required")
        return self

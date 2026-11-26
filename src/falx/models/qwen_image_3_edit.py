from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.qwen_image_3_common import (
    QwenImage3Common,
    QwenImage3ImageSize,
    QwenImage3ImageSizePreset,
)


class QwenImage3EditConfig(QwenImage3Common):
    app_id: Literal["alibaba/qwen-image-3/edit"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description=(
            "Text prompt describing the desired edit. Supports Chinese and English. "
            "Max 5000 characters."
        ),
    )
    image_size: QwenImage3ImageSizePreset | QwenImage3ImageSize | None = Field(
        default=None,
        description=(
            "The size of the generated image. If not provided, the model determines "
            "the resolution automatically. Total number of pixels must be between "
            "512x512 and 2048x2048."
        ),
    )
    image_urls: list[str] = Field(
        ...,
        description=(
            "Reference images for editing (1-3 images required). Order matters: "
            "reference as 'image 1', 'image 2', 'image 3' in prompt. Resolution: "
            "384-2048px each dimension. Max size: 10MB each. Formats: JPEG, JPG, PNG "
            "(no alpha), WEBP."
        ),
    )

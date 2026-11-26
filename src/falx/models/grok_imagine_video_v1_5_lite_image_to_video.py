from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models.grok_imagine_video_v1_5_lite_common import (
    GrokImagineVideoV15LiteBaseConfig,
    GrokImagineVideoV15LiteKeyframe,
)


class GrokImagineVideoV15LiteImageToVideoConfig(GrokImagineVideoV15LiteBaseConfig):
    """``grok-imagine-video-1.5`` image-to-video (no ``aspect_ratio``).

    Widens ``resolution`` to add the 1080p tier supported by the 1.5 model
    (the standard model remains 480p/720p only).
    """

    app_id: Literal["xai/grok-imagine-video/v1.5/lite/image-to-video"]
    prompt: str = Field(
        ...,
        max_length=4096,
        description="Text description of desired changes or motion in the video.",
    )
    image_url: str = Field(
        ...,
        description="URL of the input image for video generation.",
    )
    end_image_url: str | None = Field(
        default=None,
        description=(
            "URL of an image to pin as the exact last frame. Supported on Grok Imagine "
            "Video 1.5 (not Lite). Billed as an additional input image."
        ),
    )
    keyframes: list[GrokImagineVideoV15LiteKeyframe] | None = Field(
        default=None,
        max_length=4,
        description=(
            "Up to 4 images pinned at exact times strictly inside the clip. Supported on "
            "Grok Imagine Video 1.5 (not Lite). Each is billed as an additional input image."
        ),
    )

    @model_validator(mode="after")
    def validate_keyframe_timestamps(self) -> Self:
        if self.keyframes is not None and any(
            keyframe.timestamp >= self.duration for keyframe in self.keyframes
        ):
            raise ValueError("keyframe timestamp must be strictly less than duration")
        return self

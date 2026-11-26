from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.vidu_q4_common import ViduQ4BaseConfig


class ViduQ4ReferenceToVideoConfig(ViduQ4BaseConfig):
    app_id: Literal["fal-ai/vidu/q4/reference-to-video"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description=(
            "Text prompt for video generation, max 5000 characters. Refer to references "
            "by their position in the lists: [@reference_image_1], [@reference_image_2], "
            "... for images and [reference_audio_1], [reference_audio_2], ... for audio clips."
        ),
    )
    reference_image_urls: list[str] = Field(
        default_factory=list,
        max_length=12,
        description=(
            "URLs or base64 data URIs of up to 12 reference images (png, jpeg, jpg, webp) "
            "used to keep subjects consistent."
        ),
    )
    reference_audio_urls: list[str] = Field(
        default_factory=list,
        max_length=3,
        description=(
            "URLs or base64 data URIs of up to 3 mp3 reference audio clips "
            "(3-12 seconds each, max 50 MB) used to keep voices consistent."
        ),
    )
    aspect_ratio: Literal["16:9", "9:16", "4:3", "3:4", "1:1"] = Field(
        default="16:9",
        description="The aspect ratio of the output video",
    )
    audio: bool = Field(
        default=False,
        description=(
            "Whether to generate audio (dialogue and sound effects) with the video. "
            "When false, the output video is silent."
        ),
    )

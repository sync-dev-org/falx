from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models.seedance_us_common import SeedanceUsVideoConfig


class Seedance2UsReferenceToVideoConfig(SeedanceUsVideoConfig):
    app_id: Literal["bytedance/seedance-2.0/us/reference-to-video"]
    prompt: str = Field(..., description="The text prompt used to generate the video.")
    image_urls: list[str] = Field(
        default_factory=list,
        max_length=9,
        description=(
            "Reference images to guide video generation. Refer to them in the prompt as "
            "@Image1, @Image2, etc. Supported formats: JPEG, PNG, WebP, BMP, TIFF, GIF, "
            "HEIC, HEIF. Max 30 MB per image. Up to 9 images. Total files across all "
            "modalities must not exceed 12."
        ),
    )
    video_urls: list[str] = Field(
        default_factory=list,
        max_length=3,
        description=(
            "Reference videos to guide video generation. Refer to them in the prompt as "
            "@Video1, @Video2, etc. Supported formats: MP4, MOV. Up to 3 videos, combined "
            "duration must be between 2 and 15 seconds, total size under 50 MB. Each video "
            "must be between ~480p (640x640) and ~720p (834x1112) in resolution."
        ),
    )
    audio_urls: list[str] = Field(
        default_factory=list,
        max_length=3,
        description=(
            "Reference audio to guide video generation. Refer to them in the prompt as "
            "@Audio1, @Audio2, etc. Supported formats: MP3, WAV. Up to 3 files, combined "
            "duration must not exceed 15 seconds. Max 15 MB per file. At least one "
            "reference image or video is required."
        ),
    )

    @model_validator(mode="after")
    def validate_reference_file_constraints(self) -> Self:
        image_count = len(self.image_urls)
        video_count = len(self.video_urls)
        audio_count = len(self.audio_urls)

        if image_count + video_count + audio_count > 12:
            raise ValueError(
                "total files across image_urls, video_urls, and audio_urls must be <= 12"
            )
        if audio_count > 0 and image_count == 0 and video_count == 0:
            raise ValueError("audio_urls require image_urls or video_urls")
        return self

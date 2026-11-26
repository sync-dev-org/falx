from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class Seedance25ReferenceToVideoConfig(BaseFalConfig):
    app_id: Literal["bytedance/seedance-2.5/reference-to-video"]
    prompt: str = Field(
        ...,
        description="The text prompt used to generate the video.",
    )
    image_urls: list[str] = Field(
        default_factory=list,
        max_length=30,
        description=(
            "Reference images to guide video generation. Refer to them in the prompt as "
            "@Image1, @Image2, etc. Supported formats: JPG, PNG, WebP, BMP, TIFF, GIF, "
            "HEIC, HEIF. Max 30 MB per image. Up to 30 images. Total files across all "
            "modalities must not exceed 50."
        ),
    )
    video_urls: list[str] = Field(
        default_factory=list,
        max_length=10,
        description=(
            "Reference videos to guide video generation. Refer to them in the prompt as "
            "@Video1, @Video2, etc. Supported formats: MP4, MOV. Up to 10 videos. Each "
            "video must be 1.8 to 30.2 seconds and no larger than 200 MB; combined duration "
            "must not exceed 30.2 seconds. Dimensions must be 300 to 6,000 pixels per side, "
            "aspect ratio 0.4 to 2.5, and frame rate 24 to 60 FPS."
        ),
    )
    audio_urls: list[str] = Field(
        default_factory=list,
        max_length=10,
        description=(
            "Reference audio to guide video generation. Refer to them in the prompt as "
            "@Audio1, @Audio2, etc. Supported formats: MP3, WAV. Up to 10 files. Each file "
            "must be 1.8 to 30.2 seconds and no larger than 15 MB; combined duration must "
            "not exceed 30.2 seconds. If audio is provided, at least one reference image "
            "or video is required."
        ),
    )
    resolution: Literal["480p", "720p", "1080p"] = Field(
        default="720p",
        description=(
            "Video resolution - 480p for faster generation, 720p for balance, "
            "1080p for high quality."
        ),
    )
    duration: Literal[
        "auto",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
    ] = Field(
        default="auto",
        description=(
            "Duration of the video in seconds. Supports 4 to 30 seconds, or auto to let "
            "the model decide based on the prompt. All duration values are strings."
        ),
    )
    aspect_ratio: Literal["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="auto",
        description=(
            "The aspect ratio of the generated video. Use 16:9 for landscape, 9:16 for "
            "portrait/vertical, 1:1 for square, 21:9 for ultrawide cinematic, or auto "
            "to let the model decide."
        ),
    )
    generate_audio: bool = Field(
        default=True,
        description=(
            "Whether to generate synchronized audio for the video, including sound effects, "
            "ambient sounds, and lip-synced speech. The cost of video generation is the same "
            "regardless of whether audio is generated or not."
        ),
    )
    bitrate_mode: Literal["standard", "high"] = Field(
        default="standard",
        description=(
            "Output bitrate mode. 'high' requests a higher-quality, larger-file encode from "
            "the model; 'standard' uses the default bitrate."
        ),
    )
    end_user_id: str | None = Field(
        default=None,
        description="The unique user ID of the end user.",
    )

    @model_validator(mode="after")
    def validate_reference_file_constraints(self) -> Self:
        image_count = len(self.image_urls or [])
        video_count = len(self.video_urls or [])
        audio_count = len(self.audio_urls or [])

        if image_count + video_count + audio_count > 50:
            raise ValueError(
                "total files across image_urls, video_urls, and audio_urls must be <= 50"
            )
        if audio_count > 0 and image_count == 0 and video_count == 0:
            raise ValueError("audio_urls require image_urls or video_urls")
        return self

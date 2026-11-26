from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Seedance25ReferenceToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["bytedance/seedance-2.5/reference-to-video"]
    prompt: str | None = Field(
        default=None,
        description="The text prompt used to generate the video.",
    )
    task: Literal["auto", "reference", "editing", "extension"] = Field(
        default="reference",
        description=(
            "The type of video generation task. Reference uses the supplied media as guidance. "
            "Editing modifies a reference video and automatically coerces aspect_ratio and "
            "duration to auto. Extension continues a reference video and automatically coerces "
            "aspect_ratio to auto. Auto leaves the task type unset so the model decides it "
            "from the prompt and references."
        ),
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
            "must not exceed 30.2 seconds. An extension with a single video accepts up to "
            "120 seconds; only its last 30.2 seconds are sent to the model. Dimensions must "
            "be 300 to 6,000 pixels per side, aspect ratio 0.4 to 2.5, and frame rate 24 to 60 FPS."
        ),
    )
    audio_urls: list[str] = Field(
        default_factory=list,
        max_length=10,
        description=(
            "Reference audio to guide video generation. Refer to them in the prompt as "
            "@Audio1, @Audio2, etc. Supported formats: MP3, WAV. Up to 10 files. Each file "
            "must be 1.8 to 30.2 seconds and no larger than 15 MB; combined duration must "
            "not exceed 30.2 seconds."
        ),
    )
    resolution: Literal["480p", "720p", "1080p", "4k"] = Field(
        default="720p",
        description=(
            "Video resolution - 480p for faster generation, 720p for balance, "
            "1080p for high quality, 4k for highest quality."
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
    codec: Literal["auto", "H264", "H265"] = Field(
        default="auto",
        description=(
            "'auto' uses the default video codec; US backend output is kept unchanged. "
            "'H264' and 'H265' select H.264 and H.265 respectively."
        ),
    )
    return_last_frame: bool = Field(
        default=False,
        description="If true, also return the last frame of the generated video as an image.",
    )
    draft: bool = Field(
        default=False,
        description=(
            "Generate a draft preview at 480p, overriding resolution. Returns a draft_id "
            "for completing the draft at 1080p or 4k within 14 days."
        ),
    )
    output_format: Literal["mp4", "mov"] = Field(
        default="mp4",
        description=(
            "Output video format. 'mp4' is broadly compatible with browsers, mobile devices "
            "and media players. 'mov' targets professional post-production such as color "
            "grading, keying and compositing, but may not be supported by all players."
        ),
    )
    seed: int | None = Field(
        default=None,
        description=(
            "Random seed for reproducibility. Note that results may still vary slightly "
            "even with the same seed."
        ),
    )
    end_user_id: str | None = Field(
        default=None,
        description="The unique user ID of the end user.",
    )

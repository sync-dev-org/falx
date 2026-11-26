from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models.seedance_us_common import Seedance25UsVideoConfig


class Seedance25UsReferenceToVideoConfig(Seedance25UsVideoConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["bytedance/seedance-2.5/us/reference-to-video"]
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
    seed: int | None = Field(
        default=None,
        description=(
            "Random seed for reproducibility. Note that results may still vary slightly "
            "even with the same seed."
        ),
    )

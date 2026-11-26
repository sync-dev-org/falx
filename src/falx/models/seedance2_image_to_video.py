from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Seedance2ImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["bytedance/seedance-2.0/image-to-video"]
    prompt: str = Field(
        ...,
        description="Text prompt describing the desired motion and action for the video.",
    )
    image_url: str = Field(
        ...,
        description=(
            "URL of the starting frame image to animate. Supported formats are JPEG, PNG, and WebP."
        ),
    )
    end_image_url: str | None = Field(
        default=None,
        description=(
            "URL of the image to use as the final frame. When provided, the video "
            "transitions from the starting image to this ending image."
        ),
    )
    resolution: Literal["480p", "720p", "1080p", "4k"] = Field(
        default="720p",
        description=(
            "Video resolution. 480p is faster, 720p balances speed and quality, and "
            "1080p gives the highest quality."
        ),
    )
    duration: Literal["auto", 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] = Field(
        default="auto",
        description=(
            "Duration of the generated video in seconds. "
            "Allowed values: 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 (int) "
            "or 'auto' (string) to let the model decide based on the prompt."
        ),
    )
    aspect_ratio: Literal["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="auto",
        description=(
            "Aspect ratio of the generated video. Use auto to infer it from the input image."
        ),
    )
    generate_audio: bool = Field(
        default=True,
        description=(
            "Whether to generate synchronized audio, including sound effects, ambient "
            "sounds, and lip-synced speech."
        ),
    )
    bitrate_mode: Literal["standard", "high"] = Field(
        default="high",
        description=(
            "Output bitrate mode. high requests a higher-quality, larger-file encode; "
            "standard uses the default bitrate."
        ),
    )
    seed: int | None = Field(
        default=None,
        description=(
            "Random seed for reproducibility. Results may still vary slightly with the same seed."
        ),
    )
    end_user_id: str | None = Field(
        default=None,
        description="Unique user ID of the end user.",
    )

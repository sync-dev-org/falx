from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Seedance2MiniTextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["bytedance/seedance-2.0/mini/text-to-video"]
    prompt: str = Field(..., description="Text prompt used to generate the video.")
    resolution: Literal["480p", "720p"] = Field(
        default="720p",
        description=(
            "Video resolution. 480p is faster and 720p balances speed and quality. "
            "Mini tier does not offer 1080p or 4k."
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
            "Aspect ratio of the generated video. Use auto to let the model decide from the prompt."
        ),
    )
    generate_audio: bool = Field(
        default=True,
        description=(
            "Whether to generate synchronized audio, including sound effects, ambient "
            "sounds, and lip-synced speech."
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

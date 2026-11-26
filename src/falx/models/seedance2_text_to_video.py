from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Seedance2TextToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["bytedance/seedance-2.0/text-to-video"]
    prompt: str = Field(..., description="Text prompt used to generate the video.")
    resolution: Literal["480p", "720p", "1080p", "4k"] = Field(
        default="720p",
        description=(
            "Video resolution. 480p is faster, 720p balances speed and quality, and "
            "1080p gives the highest quality."
        ),
    )
    duration: Literal["auto", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"] = (
        Field(
            default="auto",
            description=(
                "Duration of the generated video in seconds. "
                "Allowed values: '4', '5', '6', '7', '8', '9', '10', '11', '12', "
                "'13', '14', '15' (string) or 'auto' (string) to let the model decide "
                "based on the prompt."
            ),
        )
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
    bitrate_mode: Literal["standard", "high"] = Field(
        default="standard",
        description=(
            "Output bitrate mode. high requests a higher-quality, larger-file encode; "
            "standard uses the default bitrate."
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
    end_user_id: str | None = Field(
        default=None,
        description="Unique user ID of the end user.",
    )

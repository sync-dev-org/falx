from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Seedance25TextToVideoConfig(BaseFalConfig):
    app_id: Literal["bytedance/seedance-2.5/text-to-video"]
    prompt: str = Field(
        ...,
        description="The text prompt used to generate the video.",
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

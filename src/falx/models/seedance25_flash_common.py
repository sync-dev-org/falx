from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Seedance25FlashCommon(BaseFalConfig):
    resolution: Literal["480p", "720p"] = Field(
        default="720p",
        description="Video resolution - 480p for faster generation, 720p for quality.",
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
            "the model decide based on the prompt."
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
    output_format: Literal["mp4", "mov"] = Field(
        default="mp4",
        description=(
            "Output video format. 'mp4' is broadly compatible with browsers, mobile devices "
            "and media players. 'mov' targets professional post-production such as color "
            "grading, keying and compositing, but may not be supported by all players."
        ),
    )
    return_last_frame: bool = Field(
        default=False,
        description="If true, also return the last frame of the generated video as an image.",
    )
    end_user_id: str | None = Field(
        default=None,
        description="The unique user ID of the end user.",
    )

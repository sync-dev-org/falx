from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

BriaVideoEraseOutputContainerAndCodec = Literal[
    "mp4_h265",
    "mp4_h264",
    "webm_vp9",
    "gif",
    "mov_h264",
    "mov_h265",
    "mov_proresks",
    "mkv_h264",
    "mkv_h265",
    "mkv_vp9",
    "mkv_mpeg4",
]


class BriaVideoEraseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    video_url: str = Field(
        ...,
        description="Input video to erase object from. duration must be less than 5s.",
    )
    auto_trim: bool = Field(
        default=True,
        description="auto trim the video, to working duration ( 5s )",
    )
    preserve_audio: bool = Field(
        default=True,
        description="If true, audio will be preserved in the output video.",
    )
    output_container_and_codec: BriaVideoEraseOutputContainerAndCodec = Field(
        default="mp4_h264",
        description=(
            "Output container and codec. Options: mp4_h265, mp4_h264, webm_vp9, gif, "
            "mov_h264, mov_h265, mov_proresks, mkv_h264, mkv_h265, mkv_vp9, mkv_mpeg4."
        ),
    )


class BriaVideoEraseKeypointsConfig(BriaVideoEraseConfig):
    app_id: Literal["bria/video/erase/keypoints"]
    keypoints: list[str] = Field(
        ...,
        description=(
            "Input keypoints [x,y] to erase or keep from the video. "
            "Format like so: {'x':100, 'y':100, 'type':'positive/negative'}"
        ),
    )


class BriaVideoEraseMaskConfig(BriaVideoEraseConfig):
    app_id: Literal["bria/video/erase/mask"]
    mask_video_url: str = Field(
        ...,
        description="Input video to mask erase object from. duration must be less than 5s.",
    )


class BriaVideoErasePromptConfig(BriaVideoEraseConfig):
    app_id: Literal["bria/video/erase/prompt"]
    prompt: str = Field(..., description="Input prompt to detect object to erase")

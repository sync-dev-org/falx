from __future__ import annotations

from typing import Literal

ViduQ3AspectRatio = Literal["16:9", "9:16", "4:3", "3:4", "1:1"]
ViduQ3Resolution = Literal["360p", "540p", "720p", "1080p"]

VIDU_Q3_ASPECT_RATIO_DESCRIPTION = (
    "The aspect ratio of the output video. Allowed values: '16:9', '9:16', '4:3', "
    "'3:4', '1:1' (string)."
)
VIDU_Q3_DURATION_DESCRIPTION = (
    "Duration of the video in seconds. Allowed values: integers from 1 to 16."
)
VIDU_Q3_RESOLUTION_DESCRIPTION = (
    "Output video resolution. Allowed values: '360p', '540p', '720p', '1080p' (string)."
)

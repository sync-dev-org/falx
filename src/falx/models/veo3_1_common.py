from __future__ import annotations

from typing import Literal

Veo31AspectRatio = Literal["16:9", "9:16"]
Veo31AutoAspectRatio = Literal["auto", "16:9", "9:16"]
Veo31Duration = Literal["4s", "6s", "8s"]
Veo31Resolution = Literal["720p", "1080p", "4k"]
Veo31SafetyTolerance = Literal["1", "2", "3", "4", "5", "6"]

VEO31_ASPECT_RATIO_DESCRIPTION = "Aspect ratio of the generated video"
VEO31_AUTO_ASPECT_RATIO_DESCRIPTION = "The aspect ratio of the generated video."
VEO31_DURATION_DESCRIPTION = "The duration of the generated video."
VEO31_RESOLUTION_DESCRIPTION = "The resolution of the generated video."
VEO31_SAFETY_TOLERANCE_DESCRIPTION = (
    "The safety tolerance level for content moderation. "
    "1 is the most strict (blocks most content), 6 is the least strict."
)

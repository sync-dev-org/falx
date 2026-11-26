from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.kling_v3_turbo_common import KlingV3TurboConfig


class KlingVideoV3TurboImageToVideoConfig(KlingV3TurboConfig):
    app_id: Literal[
        "fal-ai/kling-video/v3/turbo/standard/image-to-video",
        "fal-ai/kling-video/v3/turbo/pro/image-to-video",
    ]
    prompt: str | None = Field(
        default=None,
        max_length=3072,
        description=(
            "Optional text prompt. For best results keep the prompt under 2500 characters. "
            "Mutually exclusive with `multi_prompt`."
        ),
    )
    image_url: str = Field(
        ...,
        description=(
            "First-frame reference image. Formats: .jpg/.jpeg/.png; max 50MB; "
            "min 300px per side; aspect ratio within 1:2.5 to 2.5:1."
        ),
    )

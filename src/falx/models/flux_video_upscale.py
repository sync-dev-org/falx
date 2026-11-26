from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class FluxVideoUpscaleConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["blackforestlabs/flux-video-upscale"]
    video_url: str = Field(
        ...,
        description=(
            "URL of the MP4 video to upscale. The video must be at most 20 seconds and 50 MB."
        ),
    )
    upscale_factor: float = Field(
        default=2,
        ge=1.5,
        le=3,
        description="Output scaling factor. The source aspect ratio is preserved.",
    )
    creativity: Literal[0, 1] = Field(
        default=1,
        description=("Use 0 for a source-faithful upscale or 1 for creative detail enhancement."),
    )
    prompt: str | None = Field(
        default=None,
        description="Optional description used to guide creative detail enhancement.",
    )
    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=4,
        description="Moderation strictness. Lower values are stricter.",
    )

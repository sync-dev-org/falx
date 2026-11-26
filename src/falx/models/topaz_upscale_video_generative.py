from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazUpscaleVideoGenerativeConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["topaz/upscale/video/generative"]
    enable_safety_checker: bool = Field(default=True)
    video_url: str = Field(
        ...,
        description="URL of the video to upscale",
    )
    model: Literal[
        "Starlight Precise 2.6",
        "Starlight HQ",
        "Starlight Mini",
        "Starlight Sharp",
        "Starlight Fast 2",
    ] = Field(
        default="Starlight Precise 2.6",
        description=(
            "Generative diffusion enhancement model. Starlight Precise 2.6 adds realism to "
            "AI-generated video; Starlight HQ maximizes quality on high-resolution sources; "
            "Starlight Mini restores archival footage; Starlight Sharp is fast restoration "
            "with sharper detail; Starlight Fast 2 is the fastest, cheapest diffusion "
            "upscaler."
        ),
    )
    upscale_factor: float = Field(
        default=2,
        ge=1,
        le=4,
        description="Factor to upscale the video by (e.g. 2.0 doubles width and height)",
    )
    target_fps: int | None = Field(
        default=None,
        ge=16,
        le=60,
        description=(
            "Target FPS for the output. Frame interpolation is enabled only when this differs "
            "from the source FPS."
        ),
    )
    softness: float | None = Field(
        default=None,
        ge=1,
        le=5,
        description=(
            "How much softening the model applies to the output, from 1 (sharpest) to 5 "
            "(softest). Starlight Precise 2.6 only; leave unset for Topaz's default."
        ),
    )
    H264_output: bool = Field(
        default=False,
        description="Whether to use H264 codec for output video. Default is H265.",
    )

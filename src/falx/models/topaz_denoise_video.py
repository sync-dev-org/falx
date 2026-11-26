from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazDenoiseVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["topaz/denoise/video"]
    enable_safety_checker: bool = Field(default=True)
    video_url: str = Field(
        ...,
        description="URL of the video to denoise",
    )
    model: Literal["Nyx", "Nyx Fast", "Nyx XL", "Nyx HF"] = Field(
        default="Nyx",
        description=(
            "Denoise model. Nyx is high-quality denoising with texture preservation; Nyx Fast "
            "trades quality for speed on high-volume workloads; Nyx XL targets extreme noise; "
            "Nyx HF is precision denoising for pipeline-ready outputs (denoise only, no "
            "upscaling)."
        ),
    )
    upscale_factor: float = Field(
        default=1,
        ge=1,
        le=4,
        description=(
            "Optional upscale applied on top of denoising. 1.0 keeps the source resolution."
        ),
    )
    noise: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Noise reduction level (0.0-1.0). Default varies by model.",
    )
    compression: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Compression artifact removal level (0.0-1.0). Default varies by model.",
    )
    halo: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Halo reduction level (0.0-1.0). Default varies by model.",
    )
    H264_output: bool = Field(
        default=False,
        description="Whether to use H264 codec for output video. Default is H265.",
    )

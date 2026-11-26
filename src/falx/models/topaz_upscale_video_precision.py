from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazUpscaleVideoPrecisionConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["topaz/upscale/video/precision"]
    enable_safety_checker: bool = Field(default=True)
    video_url: str = Field(
        ...,
        description="URL of the video to upscale",
    )
    model: Literal[
        "Proteus",
        "Proteus Natural",
        "Iris",
        "Iris Low Quality",
        "Dione DV",
        "Dione TV",
        "Dione Robust",
        "Dione Dehalo",
        "Dione Robust Dehalo",
        "Artemis High Quality",
        "Artemis Medium Quality",
        "Artemis Low Quality",
        "Artemis Strong Halo",
        "Artemis Medium Halo",
        "Artemis Aliasing & Moire",
        "Gaia HQ",
        "Gaia CG",
        "Gaia 2",
        "Rhea",
        "Theia Fine Tune Detail",
        "Theia Fine Tune Fidelity",
    ] = Field(
        default="Proteus",
        description=(
            "Precision (non-generative) enhancement model. Proteus fits most real-world "
            "footage; Proteus Natural is a softer variant; Iris recovers faces; Dione "
            "deinterlaces legacy/interlaced sources; Artemis denoises and sharpens degraded "
            "footage; Gaia refines high-quality footage and CG (Gaia 2 upscales animation at "
            "2x); Rhea maximizes fine detail via an internal 4x pass; Theia gives manual "
            "detail/fidelity control."
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
    compression: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Compression artifact removal level (0.0-1.0). Default varies by model.",
    )
    noise: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Noise reduction level (0.0-1.0). Default varies by model.",
    )
    halo: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Halo reduction level (0.0-1.0). Default varies by model.",
    )
    grain: float | None = Field(
        default=None,
        ge=0,
        le=0.1,
        multiple_of=0.01,
        description="Film grain amount (0.0-0.1). Default varies by model.",
    )
    recover_detail: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Recover original detail level (0.0-1.0). Higher values preserve more original detail."
        ),
    )
    H264_output: bool = Field(
        default=False,
        description="Whether to use H264 codec for output video. Default is H265.",
    )

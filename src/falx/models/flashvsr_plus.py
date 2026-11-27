from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class FlashvsrPlusConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["openimaginglab/flashvsr-plus"]
    video_url: str = Field(
        ...,
        description="The input video to upscale.",
        examples=[
            "https://storage.googleapis.com/falserverless/example_inputs/birefnet-video-input.mp4"
        ],
    )
    upscale_factor: float = Field(
        default=2,
        ge=1,
        le=4,
        description="Spatial upscaling factor. Output is capped at about 4K.",
    )
    model: Literal["turbo", "base", "v1"] = Field(
        default="turbo",
        description=(
            "turbo: fastest (hybrid sliding attention). base: highest quality. v1: "
            "FlashVSR v1.1 weights with the base configuration."
        ),
    )
    temporal_compression: Literal[1, 2, 4] = Field(
        default=4,
        description=(
            "Input frames per latent frame. Use 2 or 1 for large motion; inference cost "
            "rises about 2x or 4x."
        ),
    )
    color_fix: bool = Field(
        default=False,
        description="Apply low-frequency wavelet color correction.",
    )
    preserve_audio: bool = Field(
        default=True,
        description="Copy the input audio track into the output.",
    )
    seed: int | None = Field(
        default=None,
        description="The random seed used for the generation process.",
    )
    video_output_type: Literal["X264 (.mp4)", "VP9 (.webm)", "PRORES4444 (.mov)", "GIF (.gif)"] = (
        Field(default="X264 (.mp4)", description="Output container/codec.")
    )
    video_quality: Literal["low", "medium", "high", "maximum"] = Field(
        default="high",
        description="Output encoding quality.",
    )
    video_write_mode: Literal["fast", "balanced", "small"] = Field(
        default="balanced",
        description="Output write mode.",
    )
    sync_mode: bool = Field(
        default=False,
        description="If `True`, the media will be returned inline and not stored in history.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

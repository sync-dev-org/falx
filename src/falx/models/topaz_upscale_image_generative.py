from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazUpscaleImageGenerativeConfig(BaseFalConfig):
    app_id: Literal["topaz/upscale/image/generative"]
    image_url: str = Field(
        ...,
        min_length=1,
        description="Url of the image to be upscaled",
    )
    model: Literal[
        "Wonder 3.5",
        "Wonder 3",
        "Wonder 2",
        "Wonder",
        "Recover 3",
        "Standard MAX",
        "Redefine",
        "Recovery V2",
        "Recovery",
    ] = Field(
        default="Wonder 3",
        description=(
            "Generative upscaling model. Wonder 3.5 is the latest Wonder with finer detail "
            "and fewer repetitive patterns; Wonder 3 is Topaz's most advanced generative "
            "realism model (Wonder 2/Wonder are earlier generations); Recover 3 rebuilds "
            "natural detail; Standard MAX is high-quality precision-leaning upscaling; "
            "Redefine adds prompt-guided creative detail; Recovery and Recovery V2 rebuild "
            "extreme low-resolution images."
        ),
    )
    upscale_factor: float = Field(
        default=2,
        ge=1,
        le=4,
        description="Factor to upscale the image by (e.g. 2.0 doubles width and height)",
    )
    crop_to_fill: bool = Field(default=False)
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        description="Output format of the upscaled image.",
    )
    subject_detection: Literal["All", "Foreground", "Background"] = Field(
        default="All",
        description=(
            "Subject detection mode for the image enhancement. Applies to Wonder 3, "
            "Recovery and Recovery V2 models."
        ),
    )
    face_enhancement: bool = Field(
        default=True,
        description="Whether to apply face enhancement to the image.",
    )
    face_enhancement_creativity: float = Field(
        default=0,
        ge=0,
        le=1,
        description=(
            "Creativity level for face enhancement. 0.0 means no creativity, 1.0 means "
            "maximum creativity. Ignored if face enhancement is disabled."
        ),
    )
    face_enhancement_strength: float = Field(
        default=0.8,
        ge=0,
        le=1,
        description=(
            "Strength of the face enhancement. 0.0 means no enhancement, 1.0 means maximum "
            "enhancement. Ignored if face enhancement is disabled."
        ),
    )
    enhancement_strength: Literal["low", "medium", "high"] | None = Field(
        default=None,
        description=(
            "Enhancement strength for generative upscaling. Applies to Wonder 3 and Wonder "
            "3.5 models. When omitted, Topaz auto-configures it."
        ),
    )
    creativity: int | None = Field(
        default=None,
        ge=1,
        le=6,
        description=(
            "Creativity level for generative upscaling (1-6). Higher values produce more "
            "creative/hallucinated details. Applies to Redefine model only."
        ),
    )
    texture: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description=(
            "Texture detail level for generative upscaling (1-5). Applies to Redefine model "
            "only."
        ),
    )
    prompt: str | None = Field(
        default=None,
        max_length=1024,
        description=(
            "Text prompt to guide generative upscaling (max 1024 chars). Applies to Redefine "
            "model only."
        ),
    )
    autoprompt: bool | None = Field(
        default=None,
        description=(
            "Enable automatic prompt generation for generative upscaling. Applies to "
            "Redefine model only."
        ),
    )
    sharpen: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Sharpening level (0.0-1.0). Applies to Redefine model only.",
    )
    denoise: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Denoising level (0.0-1.0). Applies to Redefine model only.",
    )
    detail: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Detail recovery level (0.0-1.0). Applies to Recovery V2 model only.",
    )

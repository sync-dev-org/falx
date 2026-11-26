from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class TopazUpscaleImagePrecisionConfig(BaseFalConfig):
    app_id: Literal["topaz/upscale/image/precision"]
    image_url: str = Field(
        ...,
        min_length=1,
        description="Url of the image to be upscaled",
    )
    model: Literal[
        "Standard V2",
        "High Fidelity V3",
        "High Fidelity V2",
        "Low Resolution V2",
        "CGI",
        "Text Refine",
        "Faces",
    ] = Field(
        default="Standard V2",
        description=(
            "Precision upscaling model. Standard V2 fits most photos; High Fidelity V3/V2 "
            "preserve detail in professional shots; Low Resolution V2 recovers compressed "
            "sources; CGI targets art and rendered graphics; Text Refine keeps text and "
            "shapes crisp; Faces restores facial detail with Face Recovery 3."
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
        description="Subject detection mode for the image enhancement.",
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
    sharpen: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Sharpening level (0.0-1.0). Default varies by model.",
    )
    denoise: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Denoising level (0.0-1.0). Default varies by model.",
    )
    fix_compression: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Compression artifact removal level (0.0-1.0). Not supported by the CGI model.",
    )
    strength: float | None = Field(
        default=None,
        ge=0.01,
        le=1,
        description="Enhancement strength (0.01-1.0). Applies to Text Refine model only.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class MeshyV7RetextureConfig(BaseFalConfig):
    schema_example_parameters: ClassVar[dict[str, Any]] = {
        "text_style_prompt": "<your prompt here>",
    }

    app_id: Literal["meshy/v7/retexture"]
    model_url: str = Field(
        ...,
        description=(
            "URL or base64 data URI of a 3D model to texture. Supports .glb, .gltf, .obj, .fbx, "
            ".stl formats. Can be a publicly accessible URL or data URI with MIME type "
            "application/octet-stream."
        ),
    )
    text_style_prompt: str | None = Field(
        default=None,
        max_length=800,
        description=(
            "Describe your desired texture style using text. Maximum 800 characters. Required "
            "if image_style_url is not provided."
        ),
    )
    image_style_url: str | None = Field(
        default=None,
        description=(
            "2D image to guide the texturing process. Supports .jpg, .jpeg, .png, and .webp "
            "formats. Required if text_style_prompt is not provided. If both are provided, "
            "image_style_url takes precedence."
        ),
    )
    texture_resolution: Literal["2k", "4k", "8k"] = Field(
        default="2k",
        description=(
            "Base color resolution: 2k (2048), 4k (4096), or 8k (8192). 4k and 8k require Meshy "
            "6 or 7. At 8k, PBR maps are 4k and no emission map is generated."
        ),
    )
    enable_original_uv: bool = Field(
        default=True,
        description=(
            "Use the original UV mapping of the model instead of generating new UVs. If the "
            "model has no original UV, output quality may be reduced."
        ),
    )
    enable_pbr: bool = Field(
        default=False,
        description="Generate PBR Maps (metallic, roughness, normal) in addition to base color.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="If set to true, input data will be checked for safety before processing.",
    )

    @model_validator(mode="after")
    def validate_style_source(self) -> Self:
        if self.text_style_prompt is None and self.image_style_url is None:
            raise ValueError("text_style_prompt or image_style_url is required")
        return self

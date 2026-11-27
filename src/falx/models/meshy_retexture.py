from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.meshy_v7_retexture import MeshyV7RetextureConfig


class MeshyV6RetextureConfig(MeshyV7RetextureConfig):
    app_id: Literal["meshy/v6/retexture"]


class MeshyV6LiteRetextureConfig(MeshyV7RetextureConfig):
    app_id: Literal["meshy/v6-lite/retexture"]


class MeshyN1RetextureConfig(BaseFalConfig):
    schema_example_parameters: ClassVar[dict[str, Any]] = {
        "image_style_url": "https://example.com/input",
    }

    app_id: Literal["meshy/n1/retexture"]
    model_url: str = Field(
        default=...,
        description=(
            "URL or base64 data URI of a 3D model to texture. Supports .glb, .gltf, .obj, "
            ".fbx, .stl formats. Can be a publicly accessible URL or data URI with MIME "
            "type application/octet-stream."
        ),
    )
    image_style_url: str | None = Field(
        default=None,
        description=(
            "Single reference image, treated as the front view. Required if "
            "multiview_image_urls is not provided. Supports .jpg, .jpeg, .png, and .webp "
            "formats."
        ),
    )
    multiview_image_urls: list[str] | None = Field(
        default=None,
        min_length=1,
        max_length=4,
        description=(
            "1 to 4 reference views of the target texture (first is the front view, order "
            "of the rest is irrelevant). Cannot be combined with image_style_url."
        ),
    )
    enable_original_uv: bool = Field(
        default=True,
        description=(
            "Use the original UV mapping of the model instead of generating new UVs. If "
            "the model has no original UV, output quality may be reduced."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="If set to true, input data will be checked for safety before processing.",
    )

    @model_validator(mode="after")
    def validate_reference_source(self) -> Self:
        if (self.image_style_url is None) == (self.multiview_image_urls is None):
            raise ValueError("provide exactly one of image_style_url and multiview_image_urls")
        return self

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class MeshyReliefConfig(BaseFalConfig):
    app_id: Literal["meshy/relief"]
    image_url: str = Field(
        default=...,
        description=(
            "Photo to turn into a relief. Works best with one clear subject on a plain "
            "background. JPG, PNG or WebP up to 20 MB."
        ),
    )
    variant: Literal["low", "high"] = Field(
        default="low",
        description=(
            "Relief depth. 'low' gives slight depth and finer detail (patterns, badges, "
            "seals); 'high' gives bold, sculptural depth (pets, portraits, characters)."
        ),
    )
    should_generate_model: bool = Field(
        default=True,
        description=(
            "Generate the STL and GLB relief models. Set to false to return only the "
            "16-bit depth map."
        ),
    )
    size_mm: float = Field(
        default=60,
        ge=20,
        le=250,
        description=(
            "Length of the photo's long side in millimeters, measured flat before any bend."
        ),
    )
    carving_mode: Literal["emboss", "engrave"] = Field(
        default="emboss",
        description=(
            "'emboss' makes the nearer parts stand out; 'engrave' inverts the depth so "
            "they are cut in."
        ),
    )
    carving_depth_mm: float | None = Field(
        default=None,
        ge=0,
        le=60,
        description="Carving depth in millimeters. Defaults to 3 for 'low' and 6 for 'high'.",
    )
    remove_base: bool = Field(
        default=False,
        description=(
            "Cut away the background and build no base plate. A high removal_threshold, or "
            "a carving depth of 0, can produce an empty model."
        ),
    )
    removal_threshold: float | None = Field(
        default=None,
        ge=0.01,
        le=1,
        description=(
            "Only used with remove_base. Depth below which the background is cut, on the "
            "depth map's 0-1 scale. Defaults to 0.01."
        ),
    )
    base_thickness_mm: float | None = Field(
        default=None,
        ge=0.1,
        le=10,
        description=(
            "Base plate thickness in millimeters. Defaults to 1. Not allowed with remove_base."
        ),
    )
    bend_mode: Literal["off", "convex", "concave"] = Field(
        default="off",
        description="Bend the relief into a convex or concave curve.",
    )
    bend_axis: Literal["xz", "yz"] = Field(
        default="xz",
        description="Bend axis: 'xz' curls the left and right edges, 'yz' the top and bottom.",
    )
    bend_angle: float = Field(
        default=60,
        ge=0,
        le=360,
        description="Bend angle in degrees. Under 1 stays flat.",
    )
    mesh_resolution: int = Field(
        default=1024,
        ge=512,
        le=2048,
        description=(
            "Mesh points along the long side. At 2048, files reach about 150 MB (GLB) and "
            "300 MB (STL), and a bend can push the STL to about 800 MB."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="If set to true, input data will be checked for safety before processing.",
    )

    @model_validator(mode="after")
    def validate_base_thickness(self) -> Self:
        if self.remove_base and self.base_thickness_mm is not None:
            raise ValueError("base_thickness_mm is not allowed with remove_base")
        return self

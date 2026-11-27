from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class _LowpolyConfig(BaseFalConfig):
    face_count: int = Field(
        default=4000,
        le=10000,
        ge=200,
        description="Target number of faces in the low-poly mesh.",
    )
    geometry_file_format: Literal["fbx", "glb", "obj", "stl", "usdz"] = Field(
        default="glb",
        description="Output format. GLB, USDZ, and FBX embed textures in the file.",
    )
    rigging: bool = Field(
        default=False,
        description=(
            "Auto-rig the generated low-poly mesh and return the rigged model alongside it. Adds "
            "a second generation step, so the request takes longer."
        ),
    )
    rigging_bone_template: Literal["auto", "human", "quadruped", "bird", "dragon", "kaiju"] = Field(
        default="auto",
        description=(
            "Skeleton template for rigging. auto picks human, quadruped, bird, dragon, or kaiju "
            "from a rendered preview of the mesh. Ignored when rigging is disabled."
        ),
    )
    resolution: Literal["Basic", "High"] = Field(
        default="Basic",
        description="Texture resolution. Basic gives 2K textures and High gives 4K textures.",
    )
    mesh_mode: Literal["Quad", "Raw", "NGon"] = Field(
        default="Quad",
        description=(
            "Polygon type. Quad uses quadrilaterals, Raw uses triangles, and NGon uses polygons."
        ),
    )
    rigging_skinning_method: Literal["shell", "core"] = Field(
        default="shell",
        description=(
            "Skin weighting for rigging. shell favors smooth weights on the visible mesh for "
            "general use; core concentrates influences around the structure for precise humanoid "
            "joints. Ignored when rigging is disabled."
        ),
    )


class _LowpolyGenerationConfig(_LowpolyConfig):
    texture_mode: Literal["extreme-low", "low", "medium", "high", "extreme-high", "legacy"] = Field(
        default="medium",
        description=(
            "Texture detail. Higher levels add detail but take longer. extreme-high gives 6K "
            "textures, or 12K with High resolution. legacy uses the older texture pipeline."
        ),
    )
    uhd_texture: bool = Field(
        default=False,
        description=(
            "Double the texture resolution to sharpen fine detail. Has no effect with "
            "extreme-high. Turn it off if artifacts appear."
        ),
    )
    material: Literal["PBR", "Shaded", "Hybrid", "All", "None"] = Field(
        default="Shaded",
        description="Texture material. None returns geometry without textures.",
    )


class Hyper3dLowpolyImageTo3dConfig(_LowpolyGenerationConfig):
    app_id: Literal["hyper3d/lowpoly/image-to-3d"]
    image_urls: list[str] = Field(
        ...,
        max_length=5,
        min_length=1,
        description="One to five images of the object, used for both the mesh and the textures.",
    )
    prompt: str = Field(
        default="",
        max_length=1024,
        description=(
            "Optional description of details the images do not show clearly, such as surface "
            "materials."
        ),
    )
    image_labels: (
        list[Literal["F", "FL", "FR", "B", "BL", "BR", "L", "R", "U", "D", "?"]] | None
    ) = Field(
        default=None,
        max_length=5,
        description=(
            "Optional viewing direction of each image, in image_urls order: F front, FL "
            "front-left, FR front-right, B back, BL back-left, BR back-right, L left, R right, U "
            "top, D bottom, ? unknown. Leave empty to label every image unknown."
        ),
    )


class Hyper3dLowpolyMeshTo3dConfig(_LowpolyConfig):
    app_id: Literal["hyper3d/lowpoly/mesh-to-3d"]
    model_url: str = Field(
        ...,
        min_length=1,
        description="URL of the mesh to simplify: OBJ, GLB, STL, FBX, USD, USDA, USDZ, or USDC.",
    )
    transfer_texture: bool = Field(
        default=True,
        description=(
            "Transfer the original textures to the simplified mesh. Disable to return geometry "
            "only."
        ),
    )


class Hyper3dLowpolyTextTo3dConfig(_LowpolyGenerationConfig):
    app_id: Literal["hyper3d/lowpoly/text-to-3d"]
    prompt: str = Field(
        ...,
        max_length=1024,
        pattern="\\S",
        description="Text description of the object to generate.",
    )

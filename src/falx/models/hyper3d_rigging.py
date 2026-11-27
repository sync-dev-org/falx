from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from falx.models import BaseFalConfig


class Hyper3dRigHierarchyNode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(
        ...,
        min_length=1,
        pattern="\\S",
        description="Bone name.",
    )
    length: float | None = Field(
        default=None,
        gt=0,
        description=(
            "Bone length along local +Y in input model units. Omit for automatic calculation; "
            "explicit null is not accepted."
        ),
    )
    parent: int = Field(
        ...,
        ge=-1,
        description="Parent node index, or -1 for the root.",
    )
    transform: list[float] | None = Field(
        default=None,
        description="Optional flat bone transform in input model coordinates.",
    )

    @field_validator("length")
    @classmethod
    def reject_explicit_null_length(cls, value: float | None) -> float:
        if value is None:
            raise ValueError("length cannot be explicitly null; omit it for automatic calculation")
        return value


class Hyper3dRiggingConfig(BaseFalConfig):
    app_id: Literal["hyper3d/rigging"]
    model_url: str = Field(
        ...,
        min_length=1,
        description=(
            "URL of a self-contained mesh with embedded resources: OBJ, GLB, STL, FBX, USD, "
            "USDA, USDZ, or USDC. Geometry, embedded materials, and textures are preserved "
            "without remeshing or texture generation. **Important**: Before uploading, ensure "
            "the model uses a right-handed coordinate system with +Y up and +Z forward (the "
            "direction the character faces); +X points to the character's own left. Rigging "
            "centers and uniformly scales the model, but does not automatically rotate it to "
            "face forward. Correct the orientation before exporting and uploading."
        ),
    )
    skeleton_description: str | None = Field(
        default=None,
        pattern="\\S",
        description=(
            "Nonblank text describing anatomy and limbs. Requires bone_template=custom and "
            "replaces hierarchy. Uses image_url when provided, otherwise text only."
        ),
    )
    bone_template: Literal["auto", "human", "quadruped", "bird", "dragon", "kaiju", "custom"] = (
        Field(
            default="auto",
            description=(
                "Skeleton template. auto selects human, quadruped, bird, dragon, or kaiju using "
                "image_url or a rendered model preview when no image is supplied. Presets forbid "
                "hierarchy and skeleton_description; custom requires exactly one."
            ),
        )
    )
    geometry_file_format: Literal["glb", "fbx", "usdz"] = Field(
        default="fbx",
        description="Choose one output format for the rigged mesh: GLB, FBX, or USDZ.",
    )
    animation_presets: list[str] | None = Field(
        default=None,
        max_length=10,
        description=(
            "Up to 10 distinct stock animation IDs compatible with the skeleton. Use "
            "/rigging/animations to look up IDs, names, descriptions, and loop information. "
            "Mutually exclusive with animation_urls; leave both empty for an unanimated export."
        ),
    )
    hierarchy: list[Hyper3dRigHierarchyNode] | None = Field(
        default=None,
        min_length=1,
        max_length=256,
        description=(
            "1–256 bones defining a custom skeleton as a flat list. Requires "
            "bone_template=custom; cannot accompany skeleton_description."
        ),
    )
    image_url: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Optional JPG, PNG, or WebP reference guiding automatic template selection and "
            "skeleton_description. If omitted, auto renders a model preview and "
            "skeleton_description is processed as text only. Does not trigger texture "
            "generation."
        ),
    )
    animation_urls: list[Annotated[str, Field(min_length=1)]] | None = Field(
        default=None,
        max_length=10,
        description=(
            "Up to 10 FBX URLs matching this rig, each nonempty, at most 25 MiB, and containing "
            "exactly one Take. Mutually exclusive with animation_presets; leave both empty for "
            "an unanimated export."
        ),
    )
    skinning_method: Literal["shell", "core"] = Field(
        default="shell",
        description=(
            "shell favors smooth weights on the visible mesh for general use; core concentrates "
            "influences around the structure for precise humanoid joints."
        ),
    )
    in_place: bool = Field(
        default=False,
        description=(
            "Export looping stock animations in place. Non-looping clips are unchanged. Cannot "
            "be enabled with animation_urls."
        ),
    )

    @model_validator(mode="after")
    def validate_skeleton_and_animations(self) -> Self:
        has_hierarchy = self.hierarchy is not None
        has_description = self.skeleton_description is not None
        if self.bone_template == "custom":
            if has_hierarchy == has_description:
                raise ValueError("custom requires exactly one of hierarchy or skeleton_description")
        elif has_hierarchy or has_description:
            raise ValueError("hierarchy and skeleton_description require bone_template=custom")
        if self.animation_presets and self.animation_urls:
            raise ValueError("animation_presets and animation_urls are mutually exclusive")
        if self.animation_presets and len(set(self.animation_presets)) != len(
            self.animation_presets
        ):
            raise ValueError("animation_presets must contain distinct animation IDs")
        if self.in_place and self.animation_urls:
            raise ValueError("in_place cannot be enabled with animation_urls")
        return self


class Hyper3dRiggingAnimationsConfig(BaseFalConfig):
    app_id: Literal["hyper3d/rigging/animations"]
    category: (
        Literal[
            "human",
            "canine",
            "bird",
            "fish",
            "heavyhooved",
            "leanhooved",
            "lizard",
            "rodentia",
            "seaturtle",
        ]
        | None
    ) = Field(
        default=None,
        description="Filter stock animations by category. Omit to list all categories.",
    )

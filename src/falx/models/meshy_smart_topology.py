from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class _MeshySmartTopologyConfig(BaseFalConfig):
    target_polycount: int = Field(
        default=15000,
        ge=100,
        le=30000,
        description=(
            "Target number of triangles in the generated model. Smart Topology output is "
            "triangle-only."
        ),
    )
    pose_mode: Literal["a-pose", "t-pose", ""] = Field(
        default="",
        description=(
            "Pose mode for the generated model. 'a-pose' generates an A-pose, 't-pose' "
            "generates a T-pose, empty string for no specific pose."
        ),
    )
    enable_rigging: bool = Field(
        default=False,
        description=(
            "Automatically rig the generated model as a humanoid character. Includes basic "
            "walking and running animations. Best results with humanoid characters that "
            "have clearly defined limbs."
        ),
    )
    rigging_height_meters: float = Field(
        default=1.7,
        gt=0,
        description=(
            "Approximate height of the character in meters. Only used when enable_rigging is true."
        ),
    )
    skeleton_template: (
        Literal[
            "mixamo",
            "ue5_mannequin",
            "unity_humanoid",
            "maya_human_ik",
            "blender_rigify_basic_human",
            "max_biped",
            "cc5_hd_neutral_base",
            "daz_genesis9",
            "meshyrig",
        ]
        | None
    ) = Field(
        default=None,
        description=(
            "Skeleton template for the rig. Animations made from the rig use the same "
            "skeleton. Leave unset for Meshy's default skeleton (meshyrig). Some models "
            "can only be rigged on meshyrig without fingers; those requests fail with a "
            "422. Only used when enable_rigging is true."
        ),
    )
    include_fingers: bool = Field(
        default=False,
        description=(
            "Rig the character's fingers. Works with any skeleton template. Only used when "
            "enable_rigging is true."
        ),
    )
    enable_animation: bool = Field(
        default=False,
        description=(
            "Apply an animation preset to the rigged model. Requires enable_rigging to be true."
        ),
    )
    animation_action_id: int = Field(
        default=92,
        description=(
            "Animation preset ID from Meshy's library. Only used when enable_animation is "
            "true; in that case it must be in [0, 696]. See "
            "https://docs.meshy.ai/en/api/animation-library for available action IDs."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="If set to true, input data will be checked for safety before processing.",
    )

    @model_validator(mode="after")
    def validate_animation(self) -> Self:
        if self.enable_animation:
            if not self.enable_rigging:
                raise ValueError("enable_animation requires enable_rigging to be true")
            if not 0 <= self.animation_action_id <= 696:
                raise ValueError("animation_action_id must be between 0 and 696")
        return self


class MeshyT25ImageTo3dConfig(_MeshySmartTopologyConfig):
    app_id: Literal["meshy/t2.5/image-to-3d"]
    image_url: str = Field(
        default=...,
        description=(
            "Image URL or base64 data URI for 3D model creation. Supports .jpg, .jpeg, and "
            ".png formats. Also supports AVIF and HEIF formats which will be automatically "
            "converted."
        ),
    )
    should_texture: bool = Field(
        default=True,
        description="Whether to generate textures",
    )
    texture_model: Literal["default", "meshy-7", "meshy-n1", "meshy-6-lite"] = Field(
        default="default",
        description=(
            "Model that textures the generated mesh, in the same task. 'default' uses "
            "Meshy's default texture model for T2/T2.5 (Meshy 7). Ignored when "
            "should_texture is false. meshy-n1 makes a 2K base color texture from "
            "reference images only: it rejects texture_prompt and enable_pbr. With "
            "meshy-n1, texture_image_url is used as the front view, or the input image "
            "when it is unset."
        ),
    )
    enable_pbr: bool = Field(
        default=False,
        description="Generate PBR Maps (metallic, roughness, normal) in addition to base color",
    )
    texture_prompt: str | None = Field(
        default=None,
        max_length=800,
        description="Text prompt to guide the texturing process. Maximum 800 characters.",
    )
    texture_image_url: str | None = Field(
        default=None,
        description="2D image to guide the texturing process",
    )

    @model_validator(mode="after")
    def validate_texture_model(self) -> Self:
        if (
            self.should_texture
            and self.texture_model == "meshy-n1"
            and (self.texture_prompt is not None or self.enable_pbr)
        ):
            raise ValueError("meshy-n1 rejects texture_prompt and enable_pbr")
        return self


class MeshyT2ImageTo3dConfig(MeshyT25ImageTo3dConfig):
    app_id: Literal["meshy/t2/image-to-3d"]
    target_polycount: int = Field(
        default=4000,
        ge=100,
        le=15000,
        description=(
            "Target number of triangles in the generated model. Smart Topology output is "
            "triangle-only."
        ),
    )


class MeshyT25TextTo3dConfig(_MeshySmartTopologyConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["meshy/t2.5/text-to-3d"]
    prompt: str = Field(
        default=...,
        max_length=600,
        description="Describe what kind of object the 3D model is. Maximum 600 characters.",
    )
    mode: Literal["preview", "full"] = Field(
        default="full",
        description=(
            "Generation mode. 'preview' returns untextured Smart Topology geometry only, "
            "'full' also textures it (preview + refine)."
        ),
    )
    seed: int | None = Field(
        default=None,
        description=(
            "Seed for reproducible results. Same prompt and seed usually generate the same result."
        ),
    )
    enable_pbr: bool = Field(
        default=False,
        description="Generate PBR Maps (metallic, roughness, normal) in addition to base color.",
    )
    enable_prompt_expansion: bool = Field(
        default=False,
        description=(
            "Whether to enable prompt expansion. This will use a large language model to "
            "expand the prompt with additional details while maintaining the original "
            "meaning."
        ),
    )
    texture_prompt: str | None = Field(
        default=None,
        max_length=800,
        description=(
            "Additional text prompt to guide the texturing process (only used in 'full' "
            "mode). Maximum 800 characters. Cannot be combined with texture_image_url."
        ),
    )
    texture_image_url: str | None = Field(
        default=None,
        description=(
            "2D image to guide the texturing process (only used in 'full' mode). Cannot be "
            "combined with texture_prompt."
        ),
    )
    texture_model: Literal["meshy-7.1", "meshy-n1"] = Field(
        default="meshy-7.1",
        description=(
            "Model for the texturing (refine) step, only used in 'full' mode. meshy-n1 "
            "makes a 2K base color texture from texture_image_url, which it requires; it "
            "rejects texture_prompt and enable_pbr."
        ),
    )

    @model_validator(mode="after")
    def validate_texture_sources(self) -> Self:
        if self.mode == "full":
            if self.texture_model == "meshy-n1":
                if self.texture_prompt is not None or self.enable_pbr:
                    raise ValueError("meshy-n1 rejects texture_prompt and enable_pbr")
                if self.texture_image_url is None:
                    raise ValueError("meshy-n1 requires texture_image_url")
            if self.texture_prompt is not None and self.texture_image_url is not None:
                raise ValueError("texture_prompt cannot be combined with texture_image_url")
        return self


class MeshyT2TextTo3dConfig(MeshyT25TextTo3dConfig):
    app_id: Literal["meshy/t2/text-to-3d"]
    target_polycount: int = Field(
        default=4000,
        ge=100,
        le=15000,
        description=(
            "Target number of triangles in the generated model. Smart Topology output is "
            "triangle-only."
        ),
    )

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MeshyV7TextTo3dConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["meshy/v7/text-to-3d"]
    prompt: str = Field(
        ...,
        max_length=600,
        description="Describe what kind of object the 3D model is. Maximum 600 characters.",
    )
    mode: Literal["preview", "full"] = Field(
        default="full",
        description=(
            "Generation mode. 'preview' returns untextured geometry only, 'full' "
            "returns textured model (preview + refine)."
        ),
    )
    seed: int | None = Field(
        default=None,
        description=(
            "Seed for reproducible results. Same prompt and seed usually generate the same result."
        ),
    )
    model_type: Literal["standard"] = Field(
        default="standard",
        description=(
            "Type of 3D mesh generation. Only 'standard' is supported; Smart Topology has its "
            "own endpoints (/t2.5 and /t2)."
        ),
    )
    topology: Literal["quad", "triangle"] = Field(
        default="triangle",
        description=(
            "Specify the topology of the generated model. Quad for smooth surfaces, "
            "Triangle for detailed geometry."
        ),
    )
    target_polycount: int = Field(
        default=30_000,
        ge=100,
        le=300_000,
        description="Target number of polygons in the generated model.",
    )
    should_remesh: bool = Field(
        default=True,
        description=(
            "Whether to enable the remesh phase. When false, returns unprocessed triangular mesh."
        ),
    )
    symmetry_mode: Literal["off", "auto", "on"] = Field(
        default="auto",
        description="Controls symmetry behavior during model generation.",
    )
    enable_pbr: bool = Field(
        default=False,
        description=("Generate PBR Maps (metallic, roughness, normal) in addition to base color."),
    )
    is_a_t_pose: bool = Field(
        default=False,
        deprecated=True,
        description=("Deprecated: use pose_mode instead. When true, generates a T-pose model."),
    )
    pose_mode: Literal["a-pose", "t-pose", ""] = Field(
        default="",
        description=(
            "Pose mode for the generated model. 'a-pose' generates an A-pose, "
            "'t-pose' generates a T-pose, empty string for no specific pose."
        ),
    )
    enable_prompt_expansion: bool = Field(
        default=False,
        description=(
            "Whether to enable prompt expansion. This will use a large language model "
            "to expand the prompt with additional details while maintaining the "
            "original meaning."
        ),
    )
    texture_prompt: str | None = Field(
        default=None,
        max_length=800,
        description=(
            "Additional text prompt to guide the texturing process (only used in "
            "'full' mode). Maximum 800 characters. Cannot be combined with texture_image_url."
        ),
    )
    texture_image_url: str | None = Field(
        default=None,
        description=(
            "2D image to guide the texturing process (only used in 'full' mode). "
            "Cannot be combined with texture_prompt."
        ),
    )
    texture_model: Literal["meshy-n1"] | None = Field(
        default=None,
        description=(
            "Model for the texturing (refine) step, only used in 'full' mode. Leave unset to "
            "texture with the endpoint's model. meshy-n1 makes a 2K base color texture from a "
            "reference image only: it rejects texture_prompt, enable_pbr, and quad topology "
            "with remeshing, and needs texture_image_url unless the endpoint is v7.1 "
            "(whose preview stores a reference image)."
        ),
    )
    enable_rigging: bool = Field(
        default=False,
        description=(
            "Automatically rig the generated model as a humanoid character. Includes "
            "basic walking and running animations. Best results with humanoid "
            "characters that have clearly defined limbs."
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
            "Skeleton template for the rig. Animations made from the rig use the same skeleton. "
            "Leave unset for Meshy's default skeleton (meshyrig). Some models can only be "
            "rigged on meshyrig without fingers; those requests fail with a 422. Only used when "
            "enable_rigging is true."
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
            "Animation preset ID from Meshy's library. Only used when enable_animation "
            'is true; in that case it must be in [0, 696] (``0`` is the "Idle" preset) '
            "and is otherwise rejected with a 422. See "
            "https://docs.meshy.ai/en/api/animation-library for available action IDs."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=("If set to true, input data will be checked for safety before processing."),
    )
    geometry_resolution: Literal["standard", "2k"] | None = Field(
        default=None,
        description="Geometry resolution. Meshy-7 supports standard and 2k.",
    )
    ultra_mode: bool = Field(
        default=False,
        deprecated=True,
        description=(
            "Deprecated: use geometry_resolution='2k'. If both fields are provided, "
            "geometry_resolution takes precedence."
        ),
    )

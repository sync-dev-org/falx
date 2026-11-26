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
            "Seed for reproducible results. Same prompt and seed usually generate "
            "the same result."
        ),
    )
    model_type: Literal["standard", "lowpoly", "smart-topology"] = Field(
        default="standard",
        description=(
            "Type of 3D mesh generation. 'standard' produces a regular high-detail "
            "mesh; 'lowpoly' produces a low-poly mesh optimized for cleaner polygons; "
            "'smart-topology' uses Meshy-T2 for clean, natively separated parts on the "
            "geometry (preview) step. When set to 'lowpoly', the remesh controls "
            "(topology, target_polycount, should_remesh) are ignored by Meshy."
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
        description=(
            "Target number of polygons in the generated model. When model_type is "
            "'smart-topology' and this is left unset, Meshy's lower smart-topology "
            "default (4,000) is used instead; smart topology accepts at most 15,000."
        ),
    )
    should_remesh: bool = Field(
        default=True,
        description=(
            "Whether to enable the remesh phase. When false, returns unprocessed "
            "triangular mesh."
        ),
    )
    symmetry_mode: Literal["off", "auto", "on"] = Field(
        default="auto",
        description="Controls symmetry behavior during model generation.",
    )
    enable_pbr: bool = Field(
        default=False,
        description=(
            "Generate PBR Maps (metallic, roughness, normal) in addition to base color."
        ),
    )
    is_a_t_pose: bool = Field(
        default=False,
        deprecated=True,
        description=(
            "Deprecated: use pose_mode instead. When true, generates a T-pose model."
        ),
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
        max_length=600,
        description=(
            "Additional text prompt to guide the texturing process (only used in "
            "'full' mode)"
        ),
    )
    texture_image_url: str | None = Field(
        default=None,
        description="2D image to guide the texturing process (only used in 'full' mode)",
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
            "Approximate height of the character in meters. Only used when "
            "enable_rigging is true."
        ),
    )
    enable_animation: bool = Field(
        default=False,
        description=(
            "Apply an animation preset to the rigged model. Requires enable_rigging "
            "to be true."
        ),
    )
    animation_action_id: int = Field(
        default=92,
        description=(
            "Animation preset ID from Meshy's library. Only used when enable_animation "
            "is true; in that case it must be in [0, 696] (``0`` is the \"Idle\" preset) "
            "and is otherwise rejected with a 422. See "
            "https://docs.meshy.ai/en/api/animation-library for available action IDs."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "If set to true, input data will be checked for safety before processing."
        ),
    )
    ultra_mode: bool = Field(
        default=False,
        description=(
            "Enable higher-fidelity geometry with finer surface detail on the preview "
            "(geometry) step. Only available for standard generation (ultra requires "
            "Meshy-7; it cannot be combined with smart topology or lowpoly)."
        ),
    )

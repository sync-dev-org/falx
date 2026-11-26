from __future__ import annotations

from typing import Annotated, ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

DEFAULT_H3_MAX_CAMERA_PROMPT = (
    "The same elements in the reference are rigid. Preserve every element exactly. "
    "The entire scene is frozen. Only the camera moves. no scene motion only camera motion"
)


class H3MaxCameraKeyframe(BaseFalConfig):
    """One camera pose at a normalized point in the generated clip."""

    time: float = Field(
        ...,
        ge=0,
        le=1,
        description="Normalized video time, from 0 at the start to 1 at the end.",
    )
    azimuth: float = Field(
        ...,
        description="Horizontal camera angle around the subject, in degrees.",
    )
    elevation: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Vertical camera angle around the subject, in degrees.",
    )
    distance: float = Field(
        ...,
        gt=0,
        description="Camera distance from the subject in normalized scene units.",
    )


class H3MaxCameraPoses(BaseFalConfig):
    """Per-frame camera-to-world matrices, e.g. Blender matrix_world."""

    convention: Literal["blender", "opencv"] = Field(
        ...,
        description=(
            "Camera axes of the matrices: blender (looks down -Z, Y up) or opencv "
            "(looks down +Z, Y down). The world frame does not matter."
        ),
    )
    c2w: list[
        Annotated[
            list[Annotated[list[float], Field(min_length=4, max_length=4)]],
            Field(min_length=4, max_length=4),
        ]
    ] = Field(
        ...,
        min_length=2,
        max_length=2048,
        description="One 4x4 row-major camera-to-world matrix per frame.",
    )


class MinimaxH3MaxCameraControlsConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max/camera-controls"]
    prompt: str = Field(
        default=DEFAULT_H3_MAX_CAMERA_PROMPT,
        max_length=50_000,
        description=(
            "Text prompt for video generation. When omitted or blank, defaults to "
            "preserving the frozen reference scene while only the camera moves."
        ),
    )
    duration: float = Field(
        default=5,
        ge=0.92,
        le=15,
        description=(
            "Video length in seconds. The output can run up to about 0.7 s longer than requested."
        ),
    )
    resolution: Literal["480P", "768P", "1080P"] = Field(
        default="480P",
        description=(
            "The native generation resolution, or 1080P latent refinement from a "
            "native 768P source."
        ),
    )
    seed: int | None = Field(
        default=None,
        description="Random seed. A random seed is selected when omitted.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="If set to true, the safety checker will be enabled.",
    )
    sync_mode: bool = Field(
        default=False,
        description="Return the generated video as base64 instead of a CDN URL.",
    )
    prompt_expansion_mode: str = Field(
        ...,
        description=(
            "How much effort to spend rewriting the prompt before generation. "
            "'disabled' skips prompt expansion. 'balanced' returns in about a second. "
            "'quality' spends up to ~30s on a richer prompt."
        ),
        json_schema_extra={"default": "balanced"},
    )
    image_url: str = Field(
        ...,
        min_length=1,
        description="URL of the image to use as the first frame.",
    )
    camera_trajectory: list[H3MaxCameraKeyframe] | None = Field(
        default=None,
        min_length=2,
        max_length=12,
        description=(
            "Ordered camera keyframes. The first pose is held before its time and the "
            "final pose is held for the remainder of the video. Signed full turns are "
            "preserved, with at most 32 turns of total azimuth travel."
        ),
    )
    free_camera_preset: (
        Literal[
            "truck_right",
            "truck_left",
            "pedestal_up",
            "pedestal_down",
            "dolly_in",
            "dolly_out",
            "pan_right",
            "pan_left",
            "tilt_up",
            "tilt_down",
            "roll_right",
            "roll_left",
            "s_curve_forward",
        ]
        | None
    ) = Field(
        default=None,
        description=(
            "A fixed free-camera move. Truck, pedestal, and dolly slide the camera; "
            "pan, tilt, and roll turn it in place. The path is not editable. When "
            "this is set, camera_trajectory is ignored. Each move is one "
            "training-scale step: one near-depth unit, 30 degrees of pan, or 20 "
            "degrees of tilt or roll."
        ),
    )
    camera_poses: H3MaxCameraPoses | None = Field(
        default=None,
        description=(
            "Your own camera path, one pose per frame, e.g. sampled from a Blender "
            "camera. Poses span the whole clip evenly; only motion relative to the "
            "first pose is used. The first pose should be the camera that took "
            "image_url. When set, camera_trajectory and free_camera_preset are ignored."
        ),
    )
    camera_poses_scale: float = Field(
        default=1,
        gt=0,
        le=10000,
        description=(
            "Multiplier on imported camera translations. One model unit is the "
            "depth of the nearest scene content in the first frame, so a Blender "
            "scene whose nearest object is 5 m away needs 0.2."
        ),
    )

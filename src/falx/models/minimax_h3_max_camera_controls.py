from __future__ import annotations

from typing import ClassVar, Literal

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
    duration: int = Field(
        default=5,
        ge=5,
        le=15,
        description="The duration of the video in seconds.",
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
            "'balanced' returns in about a second. 'quality' spends up to ~30s on a "
            "richer prompt."
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

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MinimaxH3Max3dToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["minimax/h3-max/3d-to-video"]
    video_url: str = Field(
        ...,
        description="Blender video, up to 15 seconds and 32 shots, at a public HTTPS URL.",
    )
    prompt: str | None = Field(
        default=None,
        max_length=2000,
        description=(
            "Optional clarification of what your proxies represent or how they "
            "move, for example: 'The moving block represents a running person.' "
            "Camera, trajectories, timing and object count remain defined by the video."
        ),
    )
    reference_image_urls: list[str] = Field(
        default_factory=list,
        max_length=8,
        description=(
            "Optional environment, subject, interior or detail references. When "
            "supplied, uses these images directly without visual planning or "
            "generating new images; Scene Intent is optional. Without references, "
            "automatically creates appearance references within your new-image "
            "limit. Camera and movement always come from the video."
        ),
    )
    max_generated_reference_images: int = Field(
        default=2,
        ge=1,
        le=8,
        description=(
            "Maximum NEW images to generate when no reference images are supplied. "
            "Ignored when reference images are supplied. Uses fewer when enough "
            "views are covered. Uncovered shots stay in the video."
        ),
    )
    resolution: Literal["480P", "768P", "1080P"] = Field(
        default="768P",
        description="Output quality. Duration is taken automatically from the video.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

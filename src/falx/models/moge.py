from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class _MogeBaseConfig(BaseFalConfig):
    image_url: str = Field(
        default="https://storage.googleapis.com/falserverless/example_inputs/dog.png",
        description="Input RGB image to estimate geometry (point map, depth, normals) for.",
    )
    resolution_level: int = Field(
        default=9,
        ge=0,
        le=9,
        description=(
            "Processing resolution level (0-9). Higher values use more tokens for finer "
            "detail but slower inference. Output size always matches the input."
        ),
    )
    fov_x: float | None = Field(
        default=None,
        gt=0,
        le=179,
        description=(
            "Optional known horizontal field of view in degrees. If provided, MoGe uses it "
            "instead of estimating the camera FoV."
        ),
    )
    edge_threshold: float = Field(
        default=0.04,
        ge=0,
        le=1,
        description=(
            "Relative threshold for removing mesh edges across depth discontinuities. "
            "Smaller values remove more edges."
        ),
    )
    export_glb: bool = Field(
        default=True,
        description="If true, export a textured .glb mesh of the reconstructed geometry.",
    )
    export_ply: bool = Field(
        default=True,
        description="If true, export a colored .ply point cloud of the reconstructed geometry.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Enable safety checking of the input image.",
    )


class Moge2Config(_MogeBaseConfig):
    app_id: Literal["microsoft/moge-2"]
    model: Literal["vitl-normal", "vitl", "vitb-normal", "vits-normal"] = Field(
        default="vitl-normal",
        description=(
            "MoGe-2 checkpoint variant. '-normal' variants additionally predict surface "
            "normals. 'vitl' is the metric model without normals; the smaller "
            "'vitb-normal'/'vits-normal' variants trade accuracy for speed."
        ),
    )
    apply_mask: bool = Field(
        default=True,
        description=(
            "If true, mask out invalid (sky/background/uncertain) regions in the predicted "
            "point map and depth map."
        ),
    )


class Moge3Config(_MogeBaseConfig):
    app_id: Literal["microsoft/moge-3"]
    num_refinement_steps: int = Field(
        default=3,
        ge=0,
        le=5,
        description=(
            "Number of sparse 3D refinement passes over the predicted depth. 0 skips the "
            "refiner and returns the coarse MoGe-2-style prediction."
        ),
    )
    apply_mask: bool = Field(
        default=True,
        description=(
            "If true, mask out invalid (sky/background/uncertain) regions in the predicted "
            "point map, depth map and normal map."
        ),
    )

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Vggt1bConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/vggt-1b"]
    image_urls: list[str] = Field(
        default_factory=list,
        max_length=48,
        description=(
            "Input images to reconstruct. Accepts JPEG, PNG, WEBP and the other formats "
            "Pillow decodes. Images are padded to a square and resized so the longest "
            "side is 518 pixels."
        ),
    )
    video_url: str | None = Field(
        default=None,
        description=(
            "Optional input video. Frames are sampled every `frame_sampling_rate`-th "
            "frame (the first and last frames are always included) and appended after "
            "`image_urls`."
        ),
    )
    frame_sampling_rate: int = Field(
        default=24,
        ge=1,
        le=1_000,
        description=(
            "Sample every n-th frame of `video_url`. The first and last frames of the "
            "video are always included. Ignored when no video is given."
        ),
    )
    alpha_blend_onto: Literal["keep", "white", "black", "mean"] = Field(
        default="white",
        description=(
            "How to handle images with an alpha channel. 'white'/'black' composite "
            "onto that background, 'mean' composites onto the ImageNet mean RGB, and "
            "'keep' discards alpha and keeps the original pixel values."
        ),
    )
    export_prediction_data: bool = Field(
        default=True,
        description=(
            "Return one JSON file per frame with the raw model outputs (camera pose "
            "encoding, depth, depth confidence, mask)."
        ),
    )
    export_depth_maps: bool = Field(
        default=True,
        description=(
            "Return one 16-bit grayscale PNG depth raster per frame. Pixel values map "
            "linearly from `depth_range` onto 0-65535."
        ),
    )
    export_point_cloud: bool = Field(
        default=True,
        description=(
            "Return a GLB scene holding the fused coloured point cloud plus a cone mesh "
            "per estimated camera."
        ),
    )
    array_encoding: Literal["base64", "list"] = Field(
        default="base64",
        description=(
            "How arrays are encoded inside the prediction JSON files. 'base64' emits "
            "{data, shape, dtype} objects; 'list' emits nested JSON lists, which are far "
            "larger."
        ),
    )
    exclude_keys: list[
        Literal[
            "image",
            "pose_enc",
            "extrinsic",
            "intrinsic",
            "depth",
            "depth_conf",
            "mask",
            "original_image",
        ]
    ] = Field(
        default_factory=list,
        description="Keys to omit from each prediction JSON file.",
    )
    confidence_percentile: float = Field(
        default=50,
        ge=0,
        le=100,
        description=(
            "Drop this percentage of the lowest-confidence points before building the "
            "point cloud. 0 keeps every point."
        ),
    )
    max_points: int = Field(
        default=250_000,
        ge=1_000,
        le=5_000_000,
        description=(
            "Upper bound on the number of points written to the GLB. Points above the "
            "default 250,000-point budget are evenly subsampled to limit GLB "
            "serialization and upload latency."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Enable safety checking of the input images and video.",
    )

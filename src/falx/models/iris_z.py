from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig

IrisZImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
]


class IrisZImageSize(BaseFalConfig):
    width: int = Field(
        default=512,
        gt=0,
        le=14142,
        description="The width of the generated image.",
    )
    height: int = Field(
        default=512,
        gt=0,
        le=14142,
        description="The height of the generated image.",
    )


class _IrisZDepthBaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    image_url: str = Field(..., description="URL of the image to estimate depth for.")
    resolution: Literal["auto", "512", "1024"] = Field(
        default="auto",
        description=(
            "Working resolution of the model. `auto` uses 512 for images under 0.5 MP "
            "and 1024 otherwise. The depth map is returned at the input image's size."
        ),
    )
    num_inference_steps: int = Field(
        default=4,
        ge=1,
        le=16,
        description="Number of depth sampling steps.",
    )
    ensemble_size: int = Field(
        default=1,
        ge=1,
        le=10,
        description=(
            "Number of seeds whose depth predictions are aligned and median-combined. "
            "Larger ensembles are more accurate and proportionally slower; each member is billed."
        ),
    )
    seed: int | None = Field(
        default=None,
        description="Random seed. Ensemble members use consecutive seeds from this value.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )


class _IrisZGenerationBaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    num_inference_steps: int = Field(
        default=50,
        ge=1,
        le=50,
        description="The number of inference steps to perform.",
    )
    guidance_scale: float | None = Field(
        default=None,
        ge=1,
        le=20,
        description=(
            "Classifier-free guidance scale. Defaults to the model's own value "
            "(3.5 for Iris-Z, 4.0 for Iris-Z small)."
        ),
    )
    seed: int | None = Field(
        default=None,
        description=(
            "The same seed and the same prompt given to the same version of the model "
            "will output the same image every time."
        ),
    )
    output_format: Literal["png", "jpeg"] = Field(
        default="png",
        description="The format of the generated image.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "If set to true, the safety checker will be enabled. Disabling it requires "
            "account authorization; unauthorized requests are always checked, and images "
            "flagged as unsafe are returned as black images."
        ),
    )


class _IrisZDepthToImageBaseConfig(_IrisZGenerationBaseConfig):
    depth_image_url: str = Field(..., description="URL of the depth map to paint an image from.")
    depth_format: Literal["depth", "disparity", "colorized"] = Field(
        default="colorized",
        description=(
            "How to read the depth map: `depth` (bright = far), `disparity` (bright = near), "
            "or `colorized` (the colored depth image returned by this model's depth endpoints)."
        ),
    )
    prompt: str = Field(
        default="",
        max_length=4096,
        description=(
            "The prompt to generate an image from. Prompts are truncated to 512 "
            "text-encoder tokens. Leave empty for an unconditional image."
        ),
    )
    resolution: Literal["512", "1024"] = Field(
        default="1024",
        description="Output resolution tier; the depth map's aspect ratio is kept.",
    )
    seed: int | None = Field(
        default=None,
        description=(
            "The same seed, prompt and depth map given to the same version of the model "
            "will output the same image every time."
        ),
    )


class _IrisZTextBaseConfig(_IrisZGenerationBaseConfig):
    prompt: str = Field(
        ...,
        max_length=4096,
        description=(
            "The prompt to generate an image from. Prompts are truncated to 512 "
            "text-encoder tokens."
        ),
    )
    image_size: IrisZImageSize | IrisZImageSizePreset = Field(
        default="square_hd",
        description=(
            "The size of the generated image. Both sides must be multiples of 16 between "
            "256 and 2048, with at most 1310720 pixels. The model was trained at 512 and 1024."
        ),
    )


class IrisZDepthConfig(_IrisZDepthBaseConfig):
    app_id: Literal["speridlabs/iris-z"]


class IrisZSmallDepthConfig(_IrisZDepthBaseConfig):
    app_id: Literal["speridlabs/iris-z/small"]


class IrisZDepthToImageConfig(_IrisZDepthToImageBaseConfig):
    app_id: Literal["speridlabs/iris-z/depth-to-image"]


class IrisZSmallDepthToImageConfig(_IrisZDepthToImageBaseConfig):
    app_id: Literal["speridlabs/iris-z/small/depth-to-image"]


class IrisZTextToImageConfig(_IrisZTextBaseConfig):
    app_id: Literal["speridlabs/iris-z/text-to-image"]


class IrisZSmallTextToImageConfig(_IrisZTextBaseConfig):
    app_id: Literal["speridlabs/iris-z/small/text-to-image"]


class IrisZTextToRgbdConfig(_IrisZTextBaseConfig):
    app_id: Literal["speridlabs/iris-z/text-to-rgbd"]


class IrisZSmallTextToRgbdConfig(_IrisZTextBaseConfig):
    app_id: Literal["speridlabs/iris-z/small/text-to-rgbd"]

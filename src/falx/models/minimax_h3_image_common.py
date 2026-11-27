from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig

MinimaxH3ImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
]


class MinimaxH3ImageSize(BaseFalConfig):
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


class H3ImageLoraInput(BaseFalConfig):
    """A MiniMax H3-Image LoRA adapter."""

    path: str = Field(
        ...,
        description=(
            "HTTPS URL or HuggingFace repo id (owner/repo) of the LoRA safetensors file, "
            "at most 2.5 GB. Keys are `diffusion_model.<module>.lora_A.weight` / "
            "`.lora_B.weight` for the `attn.qkv_proj`, `attn.out_proj`, `mlp.fc1` and "
            "`mlp.fc2` projections of `blocks.0`-`blocks.49` and "
            "`token_refiner.blocks.0`-`1`, and optionally `condition_proj`, "
            "`video_patch_proj` and `final_layer.video_out`, as the MiniMax H3-Image "
            "trainer and ai-toolkit export."
        ),
    )
    weight_name: str | None = Field(
        default=None,
        description=(
            "Name of the LoRA weight file. Only used when `path` is a HuggingFace "
            "repo and it holds more than one LoRA."
        ),
    )
    scale: float = Field(
        default=1,
        ge=0,
        le=4,
        description="Strength of the LoRA (0.0 to 4.0).",
    )


class MinimaxH3ImageCommon(BaseFalConfig):
    """Shared image parameters for MiniMax H3-Image endpoints."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=32_000,
        description=(
            "The prompt to generate an image from. With prompt expansion on, it is "
            "rewritten into the long, complete description the model works best "
            "with; with it off, it is used verbatim."
        ),
    )
    image_size: MinimaxH3ImageSize | MinimaxH3ImageSizePreset = Field(
        default=MinimaxH3ImageSize(width=2048, height=2048),
        description=(
            "The exact output size. Output area must be 655360 to 20000000 pixels, "
            "inclusive, with aspect ratio between 1:3 and 3:1, inclusive."
        ),
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=10,
        description="The number of images to generate, all from one expanded prompt.",
    )
    output_format: Literal["jpeg", "png", "webp", "jpg"] = Field(
        default="png",
        description="The format of the generated image.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If `True`, the media will be returned as a data URI and the output data "
            "won't be available in the request history."
        ),
    )


class MinimaxH3ImageLoraCommon(BaseFalConfig):
    """LoRA parameters supported by standard MiniMax H3-Image endpoints."""

    loras: list[H3ImageLoraInput] | None = Field(
        default=None,
        max_length=4,
        description=(
            "Up to 4 LoRA adapters to apply. Requests with LoRAs bill a surcharge. "
            "With prompt expansion on, trigger words named in a LoRA's safetensors "
            "metadata (`trigger_phrase`, `modelspec.trigger_phrase` or kohya/ai-toolkit "
            "tags) are kept in the expanded prompt and never drawn as text. Keep each "
            "LoRA's trigger words in your prompt too: it follows the expanded one, "
            "unless together they exceed 32000 characters. A bare trigger word in your "
            "prompt is sent as `<trigger> style` so it is not drawn as text; quote it "
            "to have it drawn."
        ),
    )

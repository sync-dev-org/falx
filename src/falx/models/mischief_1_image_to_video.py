from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Mischief1ImageToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["tbc/mischief-1/image-to-video"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="What happens in the video. Long, specific prompts steer WAN best.",
    )
    image_url: str = Field(
        ...,
        description=(
            "http(s) URL of the condition image the video starts from, at most 25 MiB and "
            "100 megapixels. A JPEG or PNG within the endpoint's byte budget (2.5 MB by "
            "default) renders as sent; anything larger, and any other format, is re-encoded "
            "to fit (a JPEG stays JPEG, anything else becomes lossless PNG), scaled down only "
            "as far as needed and never below the requested resolution; where that resolution "
            "stops the shrink, it is sent as a JPEG of slightly lower quality instead."
        ),
    )
    resolution: Literal["480p", "720p"] = Field(
        default="720p",
        description="480p = 832x480, 720p = 1280x720 (landscape, 16 fps).",
    )
    duration: Literal[3, 5] = Field(
        default=5,
        description=(
            "Clip length in seconds: 3 or 5. Rendered at 16 fps on the model's 4N+1 frame "
            "grid, so the clip runs slightly longer than asked: 3 s -> 49 frames (3.0625 s), "
            "5 s -> 81 frames (5.0625 s). Billing follows the requested seconds, not the "
            "slightly longer rendered clip."
        ),
    )
    seed: int | None = Field(
        default=None,
        ge=0,
        le=2_147_483_647,
        description=(
            "Omit for a random seed; the seed used is echoed back. Fixes the render only: "
            "the prompt rewrite takes no seed, so send prompt_processing=original for "
            "reproducible results."
        ),
    )
    prompt_processing: Literal["original", "enhanced"] = Field(
        default="enhanced",
        description=(
            "original: render the prompt as typed (trimmed). enhanced: rewrite it against "
            "the condition image and the clip shape first. Falls back to the typed prompt "
            "when the rewrite fails or is rejected, or when rewriting is off. Either way "
            "TBC's policy service screens the prompt and the image before anything renders."
        ),
    )
    image_transform: Literal["center_crop", "resize"] = Field(
        default="center_crop",
        description=(
            "How the condition image is fitted to the render size: center_crop preserves "
            "aspect, resize stretches."
        ),
    )

from __future__ import annotations

from typing import ClassVar

from pydantic import Field, field_validator

from falx.models import BaseFalConfig


class Kandinsky6ProBaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        description="The text prompt describing the video and its sound.",
    )
    negative_prompt: str | None = Field(
        default=None,
        description="What to avoid in the video. Defaults to the model's built-in negative prompt.",
    )
    generate_audio: bool = Field(
        default=True,
        description="Whether to generate a synchronized audio track.",
    )
    enable_prompt_expansion: bool = Field(
        default=False,
        description=(
            "Whether to rewrite the prompt into a detailed video+audio description "
            "with the model's own Qwen2.5-VL text encoder before generating."
        ),
    )
    upscale_factor: float | None = Field(
        default=None,
        description=(
            "If set, upscale the generated video by this factor with Kandinsky 6 video "
            "super-resolution. One of 2, 2.25 or 4; 2.25 turns the 480p output into 1080p."
        ),
        json_schema_extra={"enum": [2, 2.25, 4, None]},
    )
    seed: int | None = Field(
        default=None,
        description="The random seed used for the generation process.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If `True`, the media will be returned as a data URI and the output data "
            "won't be available in the request history."
        ),
    )
    num_inference_steps: int = Field(
        default=50,
        ge=8,
        le=50,
        description="The number of denoising steps.",
    )
    guidance_scale: float = Field(
        default=5,
        ge=1,
        le=10,
        description="Classifier-free guidance strength.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )

    @field_validator("upscale_factor")
    @classmethod
    def validate_upscale_factor(cls, value: float | None) -> float | None:
        if value is not None and value not in (2, 2.25, 4):
            raise ValueError("upscale_factor must be 2, 2.25, 4, or null")
        return value

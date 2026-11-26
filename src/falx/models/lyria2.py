from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Lyria2Config(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["fal-ai/lyria2"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The text prompt describing the music you want to generate",
    )
    negative_prompt: str = Field(
        default="low quality",
        description="A description of what to exclude from the generated audio",
    )
    seed: int | None = Field(
        default=None,
        description=(
            "A seed for deterministic generation. If provided, the model will attempt to "
            "produce the same audio given the same prompt and other parameters."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )
